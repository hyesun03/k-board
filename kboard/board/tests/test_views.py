from django.http import HttpRequest
from django.core.urlresolvers import reverse

from .base import BoardAppTest
from board.views import new_post, post_list
from board.models import Post, Board, Comment


class CreatePostPageTest(BoardAppTest):
    def test_new_post_page_returns_correct_html(self):
        request = HttpRequest()
        request.method = 'GET'
        response = new_post(request, board_slug=self.default_board.slug)

        response_decoded = self.remove_csrf(response.content.decode())
        self.assertIn('settings_id_fields', response_decoded)

    def test_post_list_can_save_a_POST_request(self):
        request = HttpRequest()
        request.method = 'POST'
        request.POST['post_title_text'] = 'NEW POST TITLE'
        request.POST['post_content_text'] = 'NEW POST CONTENT'

        response = new_post(request, self.default_board.slug)

        self.assertEqual(Post.objects.count(), 1)
        first_new_post = Post.objects.first()
        self.assertEqual(first_new_post.title, 'NEW POST TITLE')

    def test_new_post_page_redirects_after_POST(self):
        request = HttpRequest()
        request.method = 'POST'
        request.POST['post_title_text'] = 'NEW POST TITLE'
        request.POST['post_content_text'] = 'NEW POST CONTENT'

        response = new_post(request, self.default_board.slug)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], reverse('board:post_list', args=[self.default_board.slug]))

    def test_create_post_page_only_saves_items_when_necessary(self):
        request = HttpRequest()
        new_post(request, self.default_board.slug)
        self.assertEqual(Post.objects.count(), 0)

    def test_post_list_page_displays_all_list_titles(self):
        Post.objects.create(board=self.default_board, title='turtle1', content='slow')
        Post.objects.create(board=self.default_board, title='turtle2', content='slowslow')

        request = HttpRequest()
        response = post_list(request, self.default_board.slug)

        self.assertIn('turtle1', response.content.decode())
        self.assertIn('turtle2', response.content.decode())


class PostListViewTest(BoardAppTest):
    def test_use_post_list_template(self):
        response = self.client.get(reverse('board:post_list', args=[self.default_board.slug]))
        self.assertTemplateUsed(response, 'post_list.html')

    def test_use_pagination_template(self):
        response = self.client.get(reverse('board:post_list', args=[self.default_board.slug]))
        self.assertTemplateUsed(response, 'pagination.html')


class DeletePostTest(BoardAppTest):
    def test_delete_only_post_selected_to_delete(self):
        delete_post = Post.objects.create(board=self.default_board, title='delete post', content='content')
        other_post = Post.objects.create(board=self.default_board, title='other post', content='content')

        self.assertEqual(delete_post.is_delete, False)
        self.assertEqual(other_post.is_delete, False)

        self.client.post(reverse('board:delete_post', args=[self.default_board.slug, delete_post.id]))

        delete_post.refresh_from_db()
        other_post.refresh_from_db()

        self.assertEqual(delete_post.is_delete, True)
        self.assertEqual(other_post.is_delete, False)

    def test_redirect_to_post_list_after_delete_post(self):
        delete_post = Post.objects.create(board=self.default_board, title='delete post', content='content')
        response = self.client.post(reverse('board:delete_post', args=[self.default_board.slug, delete_post.id]))

        self.assertRedirects(response, reverse('board:post_list', args=[self.default_board.slug]))

    def test_does_not_view_but_remain_in_DB_after_delete(self):
        delete_post = Post.objects.create(board=self.default_board, title='delete post', content='content')

        viewed_list = Post.objects.filter(is_delete=False)
        self.assertIn(delete_post, viewed_list)

        self.client.post(reverse('board:delete_post', args=[self.default_board.slug, delete_post.id]))

        viewed_list = Post.objects.filter(is_delete=False)
        self.assertNotIn(delete_post, viewed_list)

        all_list = Post.objects.all()
        self.assertIn(delete_post, all_list)

    def test_can_not_access_with_GET(self):
        delete_post = Post.objects.create(board=self.default_board, title='delete post', content='content')
        response = self.client.get(reverse('board:delete_post', args=[self.default_board.slug, delete_post.id]))

        self.assertEqual(response.status_code, 405)


class PostViewTest(BoardAppTest):
    def test_uses_list_template(self):
        post_ = Post.objects.create(board=self.default_board, title='post of title', content='post of content')
        response = self.client.get(reverse('board:view_post', args=[self.default_board.slug, post_.id]))
        self.assertTemplateUsed(response, 'view_post.html')

    def test_use_pagination_template(self):
        post_ = Post.objects.create(board=self.default_board, title='post of title', content='post of content')
        response = self.client.get(reverse('board:view_post', args=[self.default_board.slug, post_.id]))
        self.assertTemplateUsed(response, 'pagination.html')

    def test_passes_correct_post_to_template(self):
        other_post = Post.objects.create(
            board=self.default_board,
            title='other post of title',
            content='other post of content'
        )
        correct_post = Post.objects.create(
            board=self.default_board,
            title='correct post of title',
            content='correct post of content'
        )

        response = self.client.get(reverse('board:view_post', args=[self.default_board.slug, correct_post.id]))

        self.assertEqual(response.context['post'], correct_post)

    def test_view_post_page_displays_correct_title_and_content(self):
        other_post = Post.objects.create(
            board=self.default_board,
            title='other post of title',
            content='other post of content'
        )
        correct_post = Post.objects.create(
            board=self.default_board,
            title='correct post of title',
            content='correct post of content'
        )

        response = self.client.get(reverse('board:view_post', args=[self.default_board.slug, correct_post.id]))

        self.assertContains(response, 'correct post of title')
        self.assertContains(response, 'correct post of content')
        self.assertNotContains(response, 'other post of title')
        self.assertNotContains(response, 'other post of content')


class NewCommentTest(BoardAppTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.default_post = Post.objects.create(
            board=cls.default_board,
            title='some post title',
            content='some post content'
        )

    def test_can_create_comment(self):
        self.client.post(
            reverse('board:new_comment', args=[self.default_board.slug, self.default_post.id]),
            data={'comment_content': 'This is a comment'}
        )

        self.assertEqual(Comment.objects.count(), 1)

    def test_can_not_access_with_GET_on_new_comment(self):
        response = self.client.get(
            reverse('board:new_comment', args=[self.default_board.slug, self.default_post.id]),
            data={'comment_content': 'This is a comment'}
        )

        self.assertEqual(response.status_code, 405)


class DeleteCommentTest(BoardAppTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.default_post = Post.objects.create(
            board=cls.default_board,
            title='some post title',
            content='some post content'
        )

    def test_can_delete_comment(self):
        comment = Comment.objects.create(
            post=self.default_post,
            content='This is a comment'
        )
        response = self.client.post(
            reverse('board:delete_comment', args=[self.default_post.id]),
            data={'comment_id': comment.id}
        )

        self.assertEqual(Comment.objects.count(), 1)

    def test_can_not_access_with_GET_on_delete_comment(self):
        comment = Comment.objects.create(
            post=self.default_post,
            content='This is a comment'
        )
        response = self.client.get(
            reverse('board:delete_comment', args=[self.default_post.id]),
            data={'comment_id': comment.id}
        )

        self.assertEqual(response.status_code, 405)


# test setting : page_list_count = 10
class PostPaginationTest(BoardAppTest):
    POST_COUNT_IN_PAGE = 10

    def add_posts(self, post_count):
        for post_counter in range(0, post_count):
            post = Post()
            post.board = self.default_board
            post.title = 'POST TITLE ' + str(PostPaginationTest.POST_COUNT_IN_PAGE - post_counter + 1)
            post.content = 'POST CONTENT ' + str(PostPaginationTest.POST_COUNT_IN_PAGE - post_counter + 1)
            post.save()

    def add_pages(self, page_count):
        for page_counter in range(1, page_count+1):
            for post_counter in range(1, PostPaginationTest.POST_COUNT_IN_PAGE+1):
                post = Post()
                post.board = self.default_board
                post.title = 'POST TITLE ' + 'PAGE' + str(page_count - page_counter + 1) + ' POST' + str(PostPaginationTest.POST_COUNT_IN_PAGE - post_counter + 1)
                post.content = 'POST CONTENT ' + 'PAGE' + str(page_count - page_counter + 1) + ' POST' + str(PostPaginationTest.POST_COUNT_IN_PAGE - post_counter + 1)
                post.save()

    def get_pagination_html(self, disabled, flag, href_page=-1):
        if flag == 'previous':
            if disabled:
                return '<li class="disabled"><a><span>이전</span></a></li>'
            else:
                return '<li><a href="?page='+str(href_page)+'"><span>이전</span></a></li>'
        elif flag == 'next':
            if disabled:
                return '<li class="disabled"><a><span>다음</span></a></li>'
            else:
                return '<li><a href="?page='+str(href_page)+'"><span>다음</span></a></li>'
        elif isinstance(flag, int):
            if disabled:
                return '<li class="disabled current-page-num"><a>'+str(flag)+'</a></li>'
            else:
                return '<li class="other-page-num"><a href="?page='+str(flag)+'">'+str(flag)+'</a></li>'

    # page count = 1

    def test_view_default_page_1_for_post_count_1_when_start_board(self):
        PostPaginationTest.add_pages(self, 1)
        response = self.client.get(reverse('board:post_list', args=[self.default_board.slug]))
        self.assertContains(response, self.get_pagination_html(True, 1))

    # page count = 2
    def test_view_default_page_list_for_page_count_2_when_start_board(self):
        PostPaginationTest.add_pages(self, 2)
        response = self.client.get(reverse('board:post_list', args=[self.default_board.slug]))
        self.assertContains(response, self.get_pagination_html(True, 1))

    def test_change_page_with_click_page_1(self):
        PostPaginationTest.add_pages(self, 2)
        response = self.client.get(reverse('board:post_list', args=[self.default_board.slug])+'?page=1')
        self.assertContains(response, 'POST TITLE PAGE1 POST1')
        self.assertContains(response, self.get_pagination_html(True, 1))
        self.assertContains(response, self.get_pagination_html(False, 2))

    def test_change_page_with_click_page_2(self):
        PostPaginationTest.add_pages(self, 2)
        response = self.client.get(reverse('board:post_list', args=[self.default_board.slug])+'?page=2')
        self.assertContains(response, 'POST TITLE PAGE2 POST1')
        self.assertContains(response, self.get_pagination_html(False, 1))
        self.assertContains(response, self.get_pagination_html(True, 2))

    # page count = 13
    def test_view_default_page_list_for_page_count_13_when_start_board(self):
        PostPaginationTest.add_pages(self, 13)
        response = self.client.get(reverse('board:post_list', args=[self.default_board.slug]))
        self.assertContains(response, self.get_pagination_html(True, 1))


# test setting : comment_list_count = 10
class CommentPaginationTest(BoardAppTest):
    POST_COUNT_IN_PAGE = 5

    def add_pages(self, page_count, post):
        for page_counter in range(1, page_count+1):
            for comment_counter in range(1, CommentPaginationTest.POST_COUNT_IN_PAGE+1):
                comment = Comment()
                comment.post = post
                comment.content = 'PAGE' + str(page_count - page_counter + 1) + \
                                  ' COMMENT' + str(CommentPaginationTest.POST_COUNT_IN_PAGE - comment_counter + 1)
                comment.save()

    def get_pagination_html(self, disabled, flag, href_page=-1):
        if flag == 'previous':
            if disabled:
                return '<li class="disabled"><a><span>이전</span></a></li>'
            else:
                return '<li><a href="?page='+str(href_page)+'"><span>이전</span></a></li>'
        elif flag == 'next':
            if disabled:
                return '<li class="disabled"><a><span>다음</span></a></li>'
            else:
                return '<li><a href="?page='+str(href_page)+'"><span>다음</span></a></li>'
        elif isinstance(flag, int):
            if disabled:
                return '<li class="disabled current-page-num"><a>'+str(flag)+'</a></li>'
            else:
                return '<li class="other-page-num"><a href="?page='+str(flag)+'">'+str(flag)+'</a></li>'

    # page count = 1

    def test_view_default_page_1_for_post_count_1_when_start_board(self):
        default_post = Post.objects.create(title='title', content='content', board=self.default_board)
        CommentPaginationTest.add_pages(self, 1, default_post)
        response = self.client.get(reverse('board:view_post', args=[self.default_board.slug, default_post.id]))
        self.assertContains(response, self.get_pagination_html(True, 1))

    # page count = 2
    def test_view_default_page_list_for_page_count_2_when_start_board(self):
        default_post = Post.objects.create(title='title', content='content', board=self.default_board)
        CommentPaginationTest.add_pages(self, 2, default_post)
        response = self.client.get(reverse('board:view_post', args=[self.default_board.slug, default_post.id]))
        self.assertContains(response, self.get_pagination_html(True, 1))

    def test_change_page_with_click_page_1(self):
        default_post = Post.objects.create(title='title', content='content', board=self.default_board)
        CommentPaginationTest.add_pages(self, 2, default_post)
        response = self.client.get(reverse('board:view_post', args=[self.default_board.slug, default_post.id])+'?page=1')
        self.assertContains(response, 'PAGE1 COMMENT1')
        self.assertContains(response, self.get_pagination_html(True, 1))
        self.assertContains(response, self.get_pagination_html(False, 2))

    def test_change_page_with_click_page_2(self):
        default_post = Post.objects.create(title='title', content='content', board=self.default_board)
        CommentPaginationTest.add_pages(self, 2, default_post)
        response = self.client.get(reverse('board:view_post', args=[self.default_board.slug, default_post.id])+'?page=2')
        self.assertContains(response, 'PAGE2 COMMENT1')
        self.assertContains(response, self.get_pagination_html(False, 1))
        self.assertContains(response, self.get_pagination_html(True, 2))


    # page count = 13
    def test_view_default_page_list_for_page_count_13_when_start_board(self):
        default_post = Post.objects.create(title='title', content='content', board=self.default_board)
        CommentPaginationTest.add_pages(self, 13, default_post)
        response = self.client.get(reverse('board:view_post', args=[self.default_board.slug, default_post.id]))
        self.assertContains(response, self.get_pagination_html(True, 1))
