from rest_framework import status

from mayan.apps.documents.tests.mixins import DocumentTestMixin
from mayan.apps.rest_api.tests.base import BaseAPITestCase

from ..models import Index, IndexInstanceNode, IndexTemplateNode
from ..permissions import (
    permission_document_indexing_create, permission_document_indexing_delete,
    permission_document_indexing_edit, permission_document_indexing_view
)

from .literals import TEST_INDEX_LABEL, TEST_INDEX_SLUG
from .mixins import (
    IndexTestMixin, IndexTemplateAPIViewTestMixin,
    IndexTemplateNodeAPITestMixin
)


class IndexTemplateAPITestCase(
    IndexTestMixin, IndexTemplateAPIViewTestMixin, DocumentTestMixin,
    BaseAPITestCase
):
    auto_upload_test_document = False

    def test_index_template_create_api_view_no_permission(self):
        response = self._request_test_index_template_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(Index.objects.count(), 0)

    def test_index_template_create_api_view_with_permission(self):
        self.grant_permission(permission=permission_document_indexing_create)

        response = self._request_test_index_template_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        index = Index.objects.first()

        self.assertEqual(response.data['id'], index.pk)
        self.assertEqual(response.data['label'], index.label)

        self.assertEqual(Index.objects.count(), 1)
        self.assertEqual(index.label, TEST_INDEX_LABEL)

    def test_index_template_delete_api_view_no_permission(self):
        self._create_test_index()

        response = self._request_test_index_template_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertTrue(self.test_index in Index.objects.all())

    def test_index_template_delete_api_view_with_access(self):
        self._create_test_index()

        self.grant_access(
            obj=self.test_index, permission=permission_document_indexing_delete
        )

        response = self._request_test_index_template_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertTrue(self.test_index not in Index.objects.all())

    def test_index_template_detail_api_view_no_permission(self):
        self._create_test_index()

        response = self._request_test_index_template_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('id' not in response.data)

    def test_index_template_detail_api_view_with_access(self):
        self._create_test_index()

        self.grant_access(
            obj=self.test_index, permission=permission_document_indexing_view
        )

        response = self._request_test_index_template_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['id'], self.test_index.pk
        )

    def test_index_template_edit_via_patch_api_view_no_permission(self):
        self._create_test_index()

        response = self._request_test_index_template_edit_via_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('id' not in response.data)

    def test_index_template_edit_via_patch_api_view_with_access(self):
        self._create_test_index()

        self.grant_access(
            obj=self.test_index, permission=permission_document_indexing_edit
        )

        response = self._request_test_index_template_edit_via_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['id'], self.test_index.pk
        )


class IndexTemplateNodeAPITestCase(
    IndexTestMixin, IndexTemplateAPIViewTestMixin,
    IndexTemplateNodeAPITestMixin, DocumentTestMixin, BaseAPITestCase
):
    auto_upload_test_document = False

    def setUp(self):
        super().setUp()
        self._create_test_index()

    def test_index_template_node_no_parent_create_api_view_no_permission(self):
        index_template_node_count = IndexTemplateNode.objects.count()
        response = self._request_test_index_template_node_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(
            IndexTemplateNode.objects.count(), index_template_node_count
        )

    def test_index_template_node_no_parent_create_api_view_with_access(self):
        self.grant_access(
            obj=self.test_index, permission=permission_document_indexing_edit
        )
        index_template_node_count = IndexTemplateNode.objects.count()

        response = self._request_test_index_template_node_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            IndexTemplateNode.objects.count(), index_template_node_count
        )

    def test_index_template_node_bad_parent_create_api_view_no_permission(self):
        self._create_test_index()

        index_template_node_count = IndexTemplateNode.objects.count()
        response = self._request_test_index_template_node_create_api_view(
            extra_data={
                'parent': self.test_indexes[0].template_root.pk
            }
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(
            IndexTemplateNode.objects.count(), index_template_node_count
        )

    def test_index_template_node_bad_parent_create_api_view_with_access(self):
        self._create_test_index()

        self.grant_access(
            obj=self.test_index, permission=permission_document_indexing_edit
        )
        index_template_node_count = IndexTemplateNode.objects.count()

        response = self._request_test_index_template_node_create_api_view(
            extra_data={
                'parent': self.test_indexes[0].template_root.pk
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            IndexTemplateNode.objects.count(), index_template_node_count
        )

    def test_index_template_node_create_api_view_no_permission(self):
        index_template_node_count = IndexTemplateNode.objects.count()
        response = self._request_test_index_template_node_create_api_view(
            extra_data={
                'parent': self.test_index.template_root.pk
            }
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(
            IndexTemplateNode.objects.count(), index_template_node_count
        )

    def test_index_template_node_create_api_view_with_access(self):
        self.grant_access(
            obj=self.test_index, permission=permission_document_indexing_edit
        )
        index_template_node_count = IndexTemplateNode.objects.count()

        response = self._request_test_index_template_node_create_api_view(
            extra_data={
                'parent': self.test_index.template_root.pk
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data['id'], self.test_index_template_node.pk
        )

        self.assertEqual(
            IndexTemplateNode.objects.count(), index_template_node_count + 1
        )

    def test_index_template_node_delete_api_view_no_permission(self):
        self._create_test_index_template_node()

        index_template_node_count = IndexTemplateNode.objects.count()
        response = self._request_test_index_template_node_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(
            IndexTemplateNode.objects.count(), index_template_node_count
        )

    def test_index_template_node_delete_api_view_with_access(self):
        self._create_test_index_template_node()

        self.grant_access(
            obj=self.test_index, permission=permission_document_indexing_edit
        )
        index_template_node_count = IndexTemplateNode.objects.count()

        response = self._request_test_index_template_node_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(
            IndexTemplateNode.objects.count(), index_template_node_count - 1
        )
