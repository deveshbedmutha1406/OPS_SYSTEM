from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied, NotFound

from .models import Test, RegisteredUser


class IsTestOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        """It checks whether the test creater and the one adding mcq are same user"""
        testid = view.kwargs.get('testid', None)
        if testid is None:
            testid = request.data.get('test_id', None)
        if testid is None:
            testid = request.query_params.get('testid')
        if testid is None:
            raise PermissionDenied('test id not found in either params or request data')
        try:
            objs = Test.objects.get(testid=testid)
        except:
            raise PermissionDenied('testid does not exist')

        return objs.created_by == request.user


class IsOtherThanOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        """User who is registering should not be question setter for now just checking owner"""
        test_id = view.kwargs.get('testid', None)
        if test_id:
            try:
                test_instance = Test.objects.get(testid=test_id)
            except:
                raise PermissionDenied('no such test id exists')
            return request.user != test_instance.created_by
        return False


class IsRegisterForTest(permissions.BasePermission):

    def has_permission(self, request, view):
        """Check if user is registered to that test"""
        test_id = view.kwargs.get('testid', None)
        if test_id:
            try:
                register_user_instance = RegisteredUser.objects.get(test_id=test_id, user_id=request.user)
                return True
            except:
                raise NotFound()
        return False
