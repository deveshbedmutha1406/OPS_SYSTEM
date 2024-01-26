from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from .models import Test
class IsTestOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        """It checks whether the test creater and the one adding mcq are same user"""
        testid = view.kwargs.get('testid', None)
        if testid is None:
            testid = request.data.get('test_id', None)

        if testid is None:
            raise PermissionDenied('test id not found in either params or request data')
        try:
            objs = Test.objects.get(testid=testid)
        except:
            raise PermissionDenied('testid does not exist')

        return objs.created_by == request.user



