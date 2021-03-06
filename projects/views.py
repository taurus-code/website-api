from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from . import models, serializers


class TechnologyViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = models.Technology.objects.all()
    serializer_class = serializers.TechnologySerializer
    filter_backends = (SearchFilter,)
    search_fields = ("name",)

    def get_technology(self, request, pk=None):
        try:  # retrieve technology by primary key
            pk = int(pk)
            return get_object_or_404(self.get_queryset(), pk=pk)
        except:  # retrieve technology by slug
            return get_object_or_404(self.get_queryset().filter(slug=pk))

    def retrieve(self, request, pk=None):
        technology = self.get_technology(request, pk)
        serializer = self.get_serializer(technology)
        return Response(serializer.data)

    # detail route to return all projects built using a technology
    # .../technologies/[technology_id]|[technology_slug]/projects
    @action(detail=True, methods=["get"])
    def projects(self, request, pk=None):
        technology = self.get_technology(request, pk)
        porjects = models.Project.visible.filter(technologies__in=[technology])
        page = self.paginate_queryset(porjects)
        serializer = serializers.ProjectSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    filter_backends = (SearchFilter,)
    search_fields = (
        "name",
        "summary",
        "url_name",
        "url",
        "technologies__name",
        "tags__name",
    )

    def get_project(self, request, pk=None):
        try:  # retrieve project by primary key
            pk = int(pk)
            return get_object_or_404(self.get_queryset(), pk=pk)
        except:  # retrieve project by slug
            return get_object_or_404(self.get_queryset().filter(slug=pk))

    def get_queryset(self):
        if self.request.auth:
            return models.Project.objects.all()
        else:
            return models.Project.visible.all()

    def retrieve(self, request, pk=None):
        project = self.get_project(request, pk)
        serializer = self.get_serializer(project)
        return Response(serializer.data)
