from rest_framework import viewsets, status
from rest_framework.response import Response

from api.models import LoleidoOrganization, UserJoinOrgInvitation, UserProfile,Agent
from .serializers import (
    LoleidoOrganizationSerializer,
    UserJoinOrgInvitionSerializer
)
from api.config import DEFAULT_AGENT
class LoleidoOrganizationViewSet(viewsets.ViewSet):
    """
    组织管理
    """
    def list(self, request):
        """
        获取组织列表
        """
        user = request.user
        queryset = LoleidoOrganization.objects.filter(members__in=[user])
        serializer = LoleidoOrganizationSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        """
        创建组织
        """
        name = request.data.get("name")
        user = request.user
        try:
            loleido_organization = LoleidoOrganization.objects.create(name=name)
            loleido_organization.members.add(user)
            loleido_organization.save()
            Agent.objects.create(
                name=loleido_organization.name+"-agent",
                type=DEFAULT_AGENT["type"],
                urls = DEFAULT_AGENT["urls"],
                status = "active",
            )
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = LoleidoOrganizationSerializer(loleido_organization)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """
        获取组织详情
        """
        try:
            loleido_organization = LoleidoOrganization.objects.get(pk=pk)
        except LoleidoOrganization.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = LoleidoOrganizationSerializer(loleido_organization)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """
        更新组织
        """
        try:
            loleido_organization = LoleidoOrganization.objects.get(pk=pk)
        except LoleidoOrganization.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = LoleidoOrganizationSerializer(loleido_organization, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        """
        部分更新组织
        """
        pass

    def destroy(self, request, pk=None):
        """
        删除组织
        """
        try:
            loleido_organization = LoleidoOrganization.objects.get(pk=pk)
        except LoleidoOrganization.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        loleido_organization.delete()
        return Response(data={
            "message": "Delete success"
        },status=status.HTTP_204_NO_CONTENT)


class UserJoinOrgInviteViewSet(viewsets.ViewSet):
    """
    用户加入组织邀请
    """
    def list(self, request):
        """
        获取用户加入组织邀请列表
        """
        user = request.user
        queryset = UserJoinOrgInvitation.objects.filter(user=user)
        serializer = UserJoinOrgInvitionSerializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        """
        创建用户加入组织邀请
        """
        target_user_email = request.data.get("user_email")
        org_uuid = request.data.get("org_uuid")
        invitor = request.user
        try:
            user = UserProfile.objects.get(email=target_user_email)
        except UserProfile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            org = LoleidoOrganization.objects.get(id=org_uuid)
        except LoleidoOrganization.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        invition = UserJoinOrgInvitation.objects.create(
            user=user, loleido_organization=org,
            invitor=invitor
        )
        invition.save()
        return Response(data={
            "message": "Create success"
            },status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """
        获取用户加入组织邀请详情
        """
        try:
            invition = UserJoinOrgInvitation.objects.get(pk=pk)
        except UserJoinOrgInvitation.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if (invition.user!=request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)
        return Response(data=UserJoinOrgInvitionSerializer(invition).data, status=status.HTTP_200_OK)
            

    def update(self, request, pk=None):
        """
        更新用户加入组织邀请
        """
        try:
            invition = UserJoinOrgInvitation.objects.get(pk=pk)
        except UserJoinOrgInvitation.DoesNotExist:
            return Response({
                "message": "Not found"
            },status=status.HTTP_404_NOT_FOUND)
        if (invition.user!=request.user):
            return Response(
                {"message": "You are not the owner of the invition"},
                status=status.HTTP_403_FORBIDDEN,
            )
        if(invition.status == "accept" or invition.status == "reject"):
            return Response(
                {"message": "Invition has been processed"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if request.data.get("status") not in ["accept", "reject"]:
            return Response(
                {"message": "status should be accept or reject"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        invition.status = request.data.get("status")
        invition.save()

        if invition.status == "accept":
            print(invition.loleido_organization)
            invition.loleido_organization.members.add(invition.user)
            invition.loleido_organization.save()
            return Response(data={"message": "Accept"}, status=status.HTTP_200_OK)

        return Response(data={"message":"Reject"}, status=status.HTTP_200_OK)
