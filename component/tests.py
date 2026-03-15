import pytest
from unittest.mock import Mock, MagicMock
from rest_framework.test import APIRequestFactory
from rest_framework import status, serializers

from component.drf.viewsets import GenericViewSet
from component.drf.pagination import CustomPageNumberPagination


class TestGenericViewSet:
    def test_success_response(self):
        viewset = GenericViewSet()
        response = viewset.success_response(msg="Test success", data={"key": "value"})
        assert response.status_code == 200
        assert response.data['result'] is True
        assert response.data['code'] == '200'
        assert response.data['message'] == "Test success"
        assert response.data['data'] == {"key": "value"}

    def test_success_response_default_data(self):
        viewset = GenericViewSet()
        response = viewset.success_response()
        assert response.data['data'] == []

    def test_failure_response(self):
        viewset = GenericViewSet()
        response = viewset.failure_response(msg="Test error")
        assert response.status_code == 200
        assert response.data['result'] is False
        assert response.data['code'] == '400'
        assert response.data['message'] == "Test error"

    def test_get_page_info(self):
        viewset = GenericViewSet()
        validated_data = {'page': 2, 'page_size': 10}
        start, end = viewset.get_page_info(validated_data)
        assert start == 10
        assert end == 20

    def test_get_page_info_defaults(self):
        viewset = GenericViewSet()
        validated_data = {}
        start, end = viewset.get_page_info(validated_data)
        assert start == 0
        assert end == 5

    def test_my_paginated_response(self):
        viewset = GenericViewSet()
        validated_data = {'page': 1, 'page_size': 10}
        total_count = 25
        return_data = [{'id': 1}, {'id': 2}]
        response = viewset.my_paginated_response(validated_data, total_count, return_data)
        assert response.data['page'] == 1
        assert response.data['total_page'] == 3
        assert response.data['count'] == 25
        assert response.data['items'] == return_data


class TestCustomPageNumberPagination:
    def test_pagination_settings(self):
        paginator = CustomPageNumberPagination()
        assert paginator.page_size == 5
        assert paginator.page_size_query_param == 'page_size'
        assert paginator.max_page_size == 10000
