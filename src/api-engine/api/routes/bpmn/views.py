import logging
import os
import re
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from api.routes.bpmn.serializers import (
    BpmnBindingRecordSerializer,
    BpmnInstanceChaincodeSerializer,
    BpmnSerializer,
    BpmnInstanceSerializer,
)
import yaml
from api.config import BASE_PATH, BPMN_CHAINCODE_STORE
from api.common import ok, err
from api.models import (
    BPMN,
    BPMNInstance,
    BPMNBindingRecord,
    ChainCode,
    Environment,
    LoleidoOrganization,
    ResourceSet,
    UserProfile,
    Consortium,
    Membership,
)
from zipfile import ZipFile
import json


# from api.routes.bpmn  import BpmnCreateBody
from rest_framework import viewsets, status
from requests import get, post


class BPMNViewsSet(viewsets.ModelViewSet):

    @action(methods=["post"], detail=False, url_path="_upload")
    def upload(self, request, pk=None, *args, **kwargs):
        try:
            consortiumid = request.data.get("consortiumid")
            orgid = request.data.get("orgid")
            name = request.data.get("name")
            bpmnContent = request.data.get("bpmnContent")
            svgContent = request.data.get("svgContent")
            raw_participants = request.data.get("participants")  # [P1,P2]
            participants = [
                {"id": recordkey, "name": raw_participants[recordkey]}
                for recordkey in raw_participants.keys()
            ]
            consortium = Consortium.objects.get(id=consortiumid)
            organization = LoleidoOrganization.objects.get(id=orgid)

            bpmn = BPMN(
                # consortium = consortium,
                organization=organization,
                consortium=consortium,
                name=name,
                svgContent=svgContent,
                bpmnContent=bpmnContent,
                participants=json.dumps(participants),
            )

            bpmn.save()

            return Response(
                data=ok("bpmn file storaged success"), status=status.HTTP_202_ACCEPTED
            )

        except Exception as e:
            raise Response(err(e.args), status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["get"], detail=True, url_path="_list")
    def list_all(self, request, pk=None):
        try:
            bpmns = BPMN.objects.all()
            bpmn_data = list(bpmns.values())
            return Response(bpmn_data, status=status.HTTP_200_OK)

        except Exception as e:
            raise Response(err(e.args), status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """
        更新bpmn
        """
        try:
            bpmn = BPMN.objects.get(pk=pk)
            # bpmn.bpmnContent = request.data.get("bpmnContent")
            # bpmn.save()
        except BPMN.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        consortiumid = request.data.get("consortiumid")
        orgid = request.data.get("orgid")
        name = request.data.get("name")
        bpmnContent = request.data.get("bpmnContent")

        bpmn.organization_id = orgid
        bpmn.organization_id = orgid
        bpmn.consortium_id = consortiumid
        bpmn.name = name
        bpmn.bpmn_content = bpmnContent
        bpmn.save()

        serializer = BpmnSerializer(bpmn)
        return Response(data=ok(serializer.data), status=status.HTTP_202_ACCEPTED)

    def retrieve(self, request, pk=None, *args, **kwargs):
        """
        获取Bpmn详情
        """
        try:
            bpmn = BPMN.objects.get(pk=pk)
        except BPMN.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = BpmnSerializer(bpmn)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        """
        获取Bpmn列表
        """
        try:
            bpmns = BPMN.objects.all()
            serializer = BpmnSerializer(bpmns, many=True)
            return Response(ok(serializer.data), status=status.HTTP_200_OK)
        except Exception as e:
            raise Response(err(e.args), status=status.HTTP_400_BAD_REQUEST)


class BPMNInstanceViewSet(viewsets.ModelViewSet):
    def create(self, request, *args, **kwargs):
        """
        创建Bpmn实例
        """
        try:
            bpmn_id = request.parser_context["kwargs"].get("bpmn_id")

            try:
                bpmn = BPMN.objects.get(pk=bpmn_id)
            except BPMN.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

            try:
                env = Environment.objects.get(pk=request.data.get("env_id"))
            except Environment.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

            bpmn_instance = BPMNInstance.objects.create(
                bpmn=bpmn,
                name=request.data.get("name"),
                environment=env,
                status="Initiated",
            )
            BPMNBindingRecordViewSet()._check(bpmn_instance.id)
            serializer = BpmnInstanceSerializer(bpmn_instance)
            return Response(data=ok(serializer.data), status=status.HTTP_201_CREATED)
        except Exception as e:
            raise Response(err(e.args), status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, *args, **kwargs):
        """
        更新Bpmn实例
        """
        try:
            bpmn_instance = BPMNInstance.objects.get(pk=pk)
            if "bpmn_id" in request.data:
                bpmn_instance.bpmn_id = request.data.get("bpmn_id")
            if "name" in request.data:
                bpmn_instance.name = request.data.get("name")
            if "status" in request.data:
                bpmn_instance.status = request.data.get("status")
            if "user_id" in request.data:
                bpmn_instance.user_id = request.data.get("user_id")
            if "firefly_url" in request.data:
                bpmn_instance.firefly_url = request.data.get("firefly_url")
            bpmn_instance.save()
            serializer = BpmnInstanceSerializer(bpmn_instance)
            return Response(data=ok(serializer.data), status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            raise Response(err(e.args), status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None, *args, **kwargs):
        """
        获取Bpmn实例详情
        """
        try:
            bpmn_instance = BPMNInstance.objects.get(pk=pk)
            serializer = BpmnInstanceChaincodeSerializer(bpmn_instance)
            return Response(serializer.data)
        except BPMNInstance.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def list(self, request, *args, **kwargs):
        """
        获取Bpmn实例列表
        """
        try:
            bpmn_id = request.parser_context["kwargs"].get("bpmn_id")
            try:
                bpmn = BPMN.objects.get(pk=bpmn_id)
            except BPMN.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

            bpmn_instances = BPMNInstance.objects.filter(bpmn=bpmn)
            serializer = BpmnInstanceSerializer(bpmn_instances, many=True)
            return Response(ok(serializer.data), status=status.HTTP_200_OK)
        except Exception as e:
            raise Response(err(e.args), status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        bpmn_instance_id = request.parser_context["kwargs"].get("pk")

        try:
            bpmn_instance = BPMNInstance.objects.get(pk=bpmn_instance_id)
        except BPMNInstance.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        bpmn_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["get"], detail=True, url_path="bindInfo")
    def bind_info(self, request, pk, *args, **kwargs):
        try:
            bpmn_instance = BPMNInstance.objects.get(pk=pk)
        except BPMNInstance.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        env = bpmn_instance.environment

        def getMSPByMembershipId(membership_id):
            try:
                membership = Membership.objects.get(pk=membership_id)
            except Membership.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            resource_set = ResourceSet.objects.get(
                environment=env, membership=membership
            )
            return resource_set.sub_resource_set.get().msp

        bindings = BPMNBindingRecord.objects.filter(bpmn_instance=bpmn_instance)
        mapInfos = {
            f"{binding.participant_id}": getMSPByMembershipId(binding.membership.id)
            for binding in bindings
        }

        return Response(ok(mapInfos), status=status.HTTP_200_OK)

    def _zip_folder(self, folder_path, output_path):
        with ZipFile(output_path, "w") as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, folder_path))

    def _ends_with_time_format(self, input_string):
        pattern = r"^test-\d{4}-\d{2}-\d{2}-\d{2}\.\d{2}\.\d{2}\.bpmn$"
        if re.match(pattern, input_string):
            return True
        else:
            return False

    def _ends_with_Test(self, input_string):
        pattern = r".*Test.bpmn$"
        if re.match(pattern, input_string):
            return True
        return False

    @action(methods=["post"], detail=True, url_path="package")
    def translate(self, request, pk, *args, **kwargs):
        try:
            bpmn_instance_id = pk

            orgid = request.data.get("orgId")
            chaincodeContent = request.data.get("chaincodeContent")
            ffiContent = request.data.get("ffiContent")
            bpmn_instance = BPMNInstance.objects.get(id=bpmn_instance_id)
            env_id = bpmn_instance.environment.id

            # # 增加测试的逻辑
            bpmn = bpmn_instance.bpmn
            # if self._ends_with_time_format(bpmn.name) or self._ends_with_Test(bpmn.name):
            #     chaincodeContent = chaincodeContent.replace( # Only deal with task, not with event and gateway
            #         # "msg.MsgState = WAITFORCONFIRM", "//msg.MsgState = WAITFORCONFIRM"
            #         "gtw.GatewayState = gtwState", "//gtw.GatewayState = gtwState"
            #     )

            with open(
                BPMN_CHAINCODE_STORE + "/chaincode-go-bpmn/chaincode/smartcontract.go",
                "w",
                encoding="utf-8",
            ) as file:
                file.write(chaincodeContent)

            self._zip_folder(
                BPMN_CHAINCODE_STORE, BASE_PATH + "/opt/bpmn_chaincode.zip"
            )

            headers = request.headers
            files = {
                "file": open(file=BASE_PATH + "/opt//bpmn_chaincode.zip", mode="rb")
            }
            response = post(
                f"http://127.0.0.1:8000/api/v1/environments/{env_id}/chaincodes/package",
                data={
                    "name": bpmn.name.replace(".bpmn", "") + "-" + bpmn_instance.name,
                    "version": 1,
                    "language": "golang",
                    "org_id": orgid,
                },
                files=files,
                headers={"Authorization": headers["Authorization"]},
            )
            chaincode_id = response.json()["data"]["id"]
            chaincode = ChainCode.objects.get(id=chaincode_id)

            bpmn_instance.ffiContent = ffiContent
            bpmn_instance.chaincode_content = chaincodeContent
            bpmn_instance.chaincode = chaincode
            bpmn_instance.status = "Generated"
            # consortium = consortium,
            bpmn_instance.save()

            return Response(
                data=ok("bpmn file storaged success"), status=status.HTTP_202_ACCEPTED
            )

        except Exception as e:
            raise Response(err(e.args), status=status.HTTP_400_BAD_REQUEST)


class BPMNBindingRecordViewSet(viewsets.ModelViewSet):
    def _check(self, bpmn_instance_id):
        try:
            bpmn_instance = BPMNInstance.objects.get(pk=bpmn_instance_id)
        except BPMNInstance.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        participant_json = bpmn_instance.bpmn.participants
        participants = json.loads(participant_json)

        bindings = BPMNBindingRecord.objects.filter(bpmn_instance=bpmn_instance)

        fullfilled = len(participants) <= len(bindings)
        if fullfilled:
            bpmn_instance.status = "Fullfilled"
            bpmn_instance.save()
        return fullfilled

    def create(self, request, *args, **kwargs):
        """
        创建Bpmn绑定实例
        """
        bpmn_instance_id = request.parser_context["kwargs"].get(
            "bpmn_instance_id", None
        )
        try:
            bpmn_instance = BPMNInstance.objects.get(pk=bpmn_instance_id)
        except BPMNInstance.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        membership_id = request.data.get("membership_id", None)
        try:
            membership = Membership.objects.get(pk=membership_id)
        except Membership.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        participant_id = request.data.get("participant_id", None)

        bpmn_binding_record = BPMNBindingRecord.objects.create(
            bpmn_instance=bpmn_instance,
            membership=membership,
            participant_id=participant_id,
        )
        serializer = BpmnBindingRecordSerializer(bpmn_binding_record)
        self._check(bpmn_instance_id)
        return Response(data=ok(serializer.data), status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):

        bpmn_instance_id = request.parser_context["kwargs"].get(
            "bpmn_instance_id", None
        )
        try:
            bpmn_instance = BPMNInstance.objects.get(pk=bpmn_instance_id)
        except BPMNInstance.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        bpmn_binding_records = BPMNBindingRecord.objects.filter(
            bpmn_instance=bpmn_instance
        )

        serializer = BpmnBindingRecordSerializer(bpmn_binding_records, many=True)
        return Response(ok(serializer.data), status=status.HTTP_200_OK)
