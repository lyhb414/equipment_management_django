import pytz
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from .models import Equipment, BorrowHistory, EquipmentModification
from .serializers import EquipmentSerializer, EquipmentIdSerializer, BorrowHistorySerializer, UserSerializer, EquipmentModificationSerializer
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, get_user_model
from .permissions import IsAdminGroupUser, IsMemberGroupUser

tz = pytz.timezone('Asia/Shanghai')

#用户注册
class RegisterAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            username = request.data.get('username', None)
            if username == 0:
                return Response(
                    '用户名不能为0', 
                    status=status.HTTP_400_BAD_REQUEST,
                    content_type="application/json; charset=utf-8")

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#用户登录验证
class CheckCredentialsView(APIView):
    def post(self, request, format=None):
        data = request.data
        username = data.get('username', None)
        password = data.get('password', None)

        user = authenticate(username=username, password=password)
        if user is not None:
            member_group, created = Group.objects.get_or_create(name='Member')
            admin_group, created = Group.objects.get_or_create(name='Admin')
            user_groups = user.groups.all()
        else:
            return Response(
                "无效的用户名或密码", 
                status=status.HTTP_403_FORBIDDEN,
                content_type="application/json; charset=utf-8")

        if user:
            if user.is_superuser or member_group in user_groups or admin_group in user_groups:
                return Response(
                    '用户验证成功', 
                    status=status.HTTP_200_OK,
                    content_type="application/json; charset=utf-8")

            else:
                return Response(
                    '用户没有登录权限，请联系管理员', 
                    status=status.HTTP_400_BAD_REQUEST,
                    content_type="application/json; charset=utf-8")
        else:
            return Response(
                '用户名或密码错误', 
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json; charset=utf-8")

#获取用户姓名
class GetFirstNameView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, username, format=None):
        try:
            user = User.objects.get(username=username)
            return Response({'first_name': user.first_name}, 
                            status=status.HTTP_200_OK, 
                            content_type="application/json; charset=utf-8")
        except User.DoesNotExist:
            return Response('User not found', status=status.HTTP_404_NOT_FOUND)

#更改用户姓名
class UpdateFirstNameView(APIView):
    def put(self, request, username, format=None):
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response('User does not exist', status=status.HTTP_400_BAD_REQUEST)
        
        new_first_name = request.data.get('firstname', '')
        if new_first_name:
            user.first_name = new_first_name
            user.save()
            return Response('First name updated successfully', status=status.HTTP_200_OK)
        else:
            return Response('New first name is not provided', status=status.HTTP_400_BAD_REQUEST)
        
#授予管理员权限
class PromoteToAdminView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminGroupUser]

    def post(self, request):
        username = request.data.get('username')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response("User not found", status=status.HTTP_404_NOT_FOUND)

        admin_group, created = Group.objects.get_or_create(name='Admin')
        member_group, created = Group.objects.get_or_create(name='Member')

        user.groups.add(admin_group)
        if member_group in user.groups.all():
            user.groups.remove(member_group)

        user.save()


        return Response(
            f"{user.username} 获得了管理员权限", 
            status=status.HTTP_200_OK,
            content_type="application/json; charset=utf-8")
    
#取消管理员权限并降级为成员
class DemoteFromAdminView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminGroupUser]

    def post(self, request):
        username = request.data.get('username')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response("User not found", status=status.HTTP_404_NOT_FOUND)

        admin_group = Group.objects.get(name='Admin')
        member_group, created = Group.objects.get_or_create(name='Member')

        if admin_group in user.groups.all():
            user.groups.remove(admin_group)
            user.groups.add(member_group)
            user.save()
            return Response(
                f"{user.username} 已取消管理员权限，并降级为成员", 
                status=status.HTTP_200_OK,
                content_type="application/json; charset=utf-8",)
        else:
            return Response(f"User {user.username} is not an admin", status=status.HTTP_400_BAD_REQUEST)
    
#判断自己是否为管理员
class CheckAdminStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.is_superuser or Group.objects.get(name='Admin') in user.groups.all():
            return Response({"is_admin": True}, status=status.HTTP_200_OK)
        else:
            return Response({"is_admin": False}, status=status.HTTP_200_OK)
        
#授予成员权限
class PromoteToMemberView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminGroupUser]

    def post(self, request):
        username = request.data.get('username')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response("User not found", status=status.HTTP_404_NOT_FOUND)

        admin_group, created = Group.objects.get_or_create(name='Member')

        if user.is_superuser or Group.objects.get(name='Admin') in user.groups.all():
            return Response(
                f"User {user.username} is an admin", 
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json; charset=utf-8")
        else:
            user.groups.add(admin_group)
            user.save()

            return Response(
                f"{user.username}获得了成员权限", 
                status=status.HTTP_200_OK,
                content_type="application/json; charset=utf-8")

        
#取消成员权限
class DemoteFromMemberView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminGroupUser]

    def post(self, request):
        username = request.data.get('username')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response("User not found", status=status.HTTP_404_NOT_FOUND)

        member_group = Group.objects.get(name='Member')

        if member_group in user.groups.all():
            user.groups.remove(member_group)
            user.save()
            return Response(
                f"{user.username}已取消成员权限", 
                status=status.HTTP_200_OK,
                content_type="application/json; charset=utf-8")
        else:
            return Response(f"User {user.username} is not an member", status=status.HTTP_400_BAD_REQUEST)
    
#判断自己是否有成员权限
class CheckMemberStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.is_superuser or Group.objects.get(name='Member') in user.groups.all():
            return Response({"is_member": True}, status=status.HTTP_200_OK)
        else:
            return Response({"is_member": False}, status=status.HTTP_200_OK)



#创建器材
class EquipmentListCreate(generics.ListCreateAPIView):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    def perform_create(self, serializer):
        serializer.save(createUser=self.request.user)

        # 创建修改记录
        changed_fields = []
        for field, value in serializer.validated_data.items():
            changed_fields.append(f"{field}: '{value}'")
        equipment_modification = EquipmentModification(
            equipment_id = serializer.instance.pk,
            equipment_name = serializer.instance.name,
            username = self.request.user.username,
            user_firstname = self.request.user.first_name,
            modification_type = 0,
            modification_data = changed_fields,
        )
        if changed_fields:
            equipment_modification.save()

#器材更新、删除、检索
class EquipmentRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response = Response(serializer.data)
        response['Content-Type'] = "application/json; charset=utf-8"
        return response
    
    def patch(self, request, pk, format=None):
        user = request.user
        try:
            equipment = Equipment.objects.get(pk=pk)
        except Equipment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            itemTotalNum = request.data['totalNum']
            itemCreateUser = request.data['createUser']
        except KeyError:
            return Response(
                    "数据错误",
                    status=status.HTTP_400_BAD_REQUEST,
                    content_type="application/json; charset=utf-8",)
        
        if equipment.totalNum > itemTotalNum:
            if not user.is_superuser and not Group.objects.get(name='Admin') in user.groups.all():
                error_message = '只有管理员才能减少器材数量'
                return Response(
                    error_message,
                    status=status.HTTP_400_BAD_REQUEST,
                    content_type="application/json; charset=utf-8",
                )
            
        if equipment.createUser.username != itemCreateUser:
            if not user.is_superuser and not Group.objects.get(name='Admin') in user.groups.all():
                error_message = '只有管理员才能修改创建人'
                return Response(
                    error_message,
                    status=status.HTTP_400_BAD_REQUEST,
                    content_type="application/json; charset=utf-8",
                )

        if equipment.borrowNum > itemTotalNum:
            error_message = '修改后的总数小于已借出的数量'
            return Response(
                error_message,
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json; charset=utf-8",
            )
        
        try:
            createUser = User.objects.get(username=itemCreateUser)
            processed_itemCreateUser = createUser.pk  # 获取用户主键值
        except User.DoesNotExist:
            return Response(
                "修改后的创建人不存在", 
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json; charset=utf-8",)
        
        request.data['createUser'] = processed_itemCreateUser

        # 创建修改记录
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        changed_fields = analyze_changed_fields(instance, serializer.validated_data)
        
        equipment_modification = EquipmentModification(
            equipment_id = pk,
            equipment_name = equipment.name,
            username = user.username,
            user_firstname = user.first_name,
            modification_type = 1,
            modification_data = changed_fields,
        )
        if changed_fields:
            equipment_modification.save()

        return super().patch(request, pk, format)
    
    def delete(self, request, pk, format=None):
        try:
            equipment = Equipment.objects.get(pk=pk)
        except Equipment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        # 创建修改记录
        changed_fields = []
        for field in equipment._meta.fields:
            field_name = field.name
            field_value = getattr(equipment, field_name)
            changed_fields.append(f"{field_name}: '{field_value}'")
        
        equipment_modification = EquipmentModification(
            equipment_id = pk,
            equipment_name = equipment.name,
            username = request.user.username,
            user_firstname = request.user.first_name,
            modification_type = 2,
            modification_data = changed_fields,
        )
        equipment_modification.save()

        # 删除与此器材关联的所有借用记录
        BorrowHistory.objects.filter(itemId=equipment.id).delete()

        return super().delete(request, pk, format)
    
def analyze_changed_fields(instance, validated_data):
    changed_fields = []
    for field, value in validated_data.items():
        if getattr(instance, field) != value:
            changed_fields.append(f"{field}: {getattr(instance, field)} -> {value}")
    return changed_fields
    
#获取器材id列表
class EquipmentIdListView(ListAPIView):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentIdSerializer
    permission_classes = [permissions.IsAuthenticated]

#借用器材
class EquipmentBorrow(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, equipment_id, format=None):
        try:
            equipment = Equipment.objects.get(pk=equipment_id)
        except Equipment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            borrowDeltaNum = request.data['borrowDeltaNum']
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if equipment.totalNum - equipment.borrowNum < borrowDeltaNum :
            return Response(
                '减少数量大于空余数量',
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json; charset=utf-8",
            )
        
        if borrowDeltaNum < 0 :
            return Response(
                '借用数量需大于0',
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json; charset=utf-8",
            )

        equipment.borrowNum += borrowDeltaNum
        equipment.save()

        # 创建借用记录
        borrow_history = BorrowHistory(
            user=request.user,
            itemId=equipment_id,
            borrowNum=borrowDeltaNum,
        )
        borrow_history.save()

        return Response(status = status.HTTP_200_OK)
    
#搜索器材
class EquipmentSearchView(generics.ListAPIView):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    search_fields = ['name', 'equipId', 'createUser']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        search_by = self.request.query_params.get('search_by', 'equipId')
        query = self.request.query_params.get('query', '')
        
        if search_by == 'equipId':
            return Equipment.objects.filter(equipId__icontains=query)
        elif search_by == 'name':
            return Equipment.objects.filter(name__icontains=query)
        elif search_by == 'createUser':
            usernames = User.objects.filter(first_name__icontains=query).all()
            users = []
            for username in usernames:
                 users.append(User.objects.get(username=username))
           
            return Equipment.objects.filter(createUser__in=users)
        else:
            return Equipment.objects.none()
        
#搜索修改记录
class EquipmentModificationSearchView(generics.ListAPIView):
    queryset = EquipmentModification.objects.all()
    serializer_class = EquipmentModificationSerializer
    search_fields = ['equipment_id', 'username', 'all']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        search_by = self.request.query_params.get('search_by', 'all')
        query = self.request.query_params.get('query', '')
        
        if search_by == 'equipment_id':
            return EquipmentModification.objects.filter(equipment_id__iexact=query)
        elif search_by == 'username':
            print()
            return EquipmentModification.objects.filter(username__iexact=query)
        elif search_by == 'all':
            return EquipmentModification.objects.all()
        else:
            return EquipmentModification.objects.none()
        
#根据id获取借用记录
class BorrowHistoryDetailView(generics.RetrieveAPIView):
    queryset = BorrowHistory.objects.all()
    serializer_class = BorrowHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
        
#搜索借用记录
class BorrowHistorySearchView(generics.ListAPIView):
    queryset = BorrowHistory.objects.all()
    serializer_class = BorrowHistorySerializer
    search_fields = ['itemId']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        search_by = self.request.query_params.get('search_by', 'itemId')
        query = self.request.query_params.get('query', '')

        if search_by == 'itemId':
            return BorrowHistory.objects.filter(itemId__icontains=query)
        elif search_by == 'user':
            try:
                user = User.objects.get(username=query)
                return BorrowHistory.objects.filter(user=user)
            except User.DoesNotExist:
                return BorrowHistory.objects.none()
        else:
            return BorrowHistory.objects.none()
        
#归还器材
class ReturnEquipmentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, format=None):
        try:
            return_num = request.data['returnNum']
            history_id = request.data['historyId']
        except KeyError:
            return Response(
                '数据错误',
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json; charset=utf-8",
            )
        
        try:
            borrow_history = BorrowHistory.objects.get(id=history_id)
        except BorrowHistory.DoesNotExist:
            return Response(
                '数据错误',
                status=status.HTTP_404_NOT_FOUND,
                content_type="application/json; charset=utf-8",
            )

        if return_num <= 0:
            return Response(
                '数据错误',
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json; charset=utf-8",
            )
        
        try:
            equipment = Equipment.objects.get(pk=borrow_history.itemId)
        except Equipment.DoesNotExist:
            return Response(
                '器材未找到',
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json; charset=utf-8",
            )
        
        create_user = equipment.createUser
        if not request.user == create_user and not request.user.is_superuser and not Group.objects.get(name='Admin') in request.user.groups.all():
            return Response(
                '只能由创建人和管理员归还',
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json; charset=utf-8",
            )

        result, message = borrow_history.returnItem(return_num, request.user)
        if not result:
            return Response(message,
                            status=status.HTTP_400_BAD_REQUEST,
                            content_type="application/json; charset=utf-8",)

        return Response(message, 
                        status=status.HTTP_200_OK,
                        content_type="application/json; charset=utf-8",)
    
#归还剩余全部器材
class ReturnAllEquipmentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, format=None):
        try:
            history_id = request.data['historyId']
        except KeyError:
            return Response(
                '数据错误',
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json; charset=utf-8",
            )

        try:
            borrow_history = BorrowHistory.objects.get(id=history_id)
        except BorrowHistory.DoesNotExist:
            return Response(
                '数据错误',
                status=status.HTTP_404_NOT_FOUND,
                content_type="application/json; charset=utf-8",
            )
        
        try:
            equipment = Equipment.objects.get(pk=borrow_history.itemId)
        except Equipment.DoesNotExist:
            return Response(
                '器材未找到',
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json; charset=utf-8",
            )
        
        create_user = equipment.createUser
        if not request.user == create_user and not request.user.is_superuser and not Group.objects.get(name='Admin') in request.user.groups.all():
            return Response(
                '只能由创建人和管理员归还',
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json; charset=utf-8",
            )

        success, message = borrow_history.returnAllItem(request.user)

        if success:
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(
                message,
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json; charset=utf-8",
            )
