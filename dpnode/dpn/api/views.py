import django_filters
from rest_framework import generics, filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import DjangoModelPermissions

from dpn.api.serializers import RegistryEntrySerializer, TransferSerializer
from dpn.api.serializers import NodeSerializer
from dpn.api.permissions import IsNodeUser
from dpn.data.models import RegistryEntry, Node, Transfer, UserProfile

# Custom View Filters

class RegistryFilter(django_filters.FilterSet):
    before = django_filters.DateTimeFilter(
        name="last_modified_date",
        lookup_type='lt'
    )
    after = django_filters.DateTimeFilter(
        name="last_modified_date",
        lookup_type='gt'
    )
    first_node = django_filters.CharFilter(name="first_node__namespace")
    class Meta:
        model = RegistryEntry
        fields = ['before', 'after', 'first_node', 'object_type']

# List Views
class RegistryListView(generics.ListCreateAPIView):
    """
    Registry Entries for DPN Objects.
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (DjangoModelPermissions,)
    queryset = RegistryEntry.objects.filter(published=True)
    paginate_by = 20
    serializer_class = RegistryEntrySerializer
    filter_class = RegistryFilter

class NodeListView(generics.ListCreateAPIView):
    """
    Nodes in the DPN Network.
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (DjangoModelPermissions,)
    queryset = Node.objects.all()
    paginate_by = 20
    serializer_class = NodeSerializer

class TransferListView(generics.ListAPIView):
    """
    Transfer actions between DPN nodes.
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (DjangoModelPermissions,)

    queryset = Transfer.objects.none() # as required by model permissions
    paginate_by = 20
    serializer_class = TransferSerializer
    filter_fields = ("status", "fixity", "valid")
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('created_on', 'updated_on')

    def get_queryset(self):
        profile = UserProfile.objects.get(user=self.request.user)
        return Transfer.objects.filter(node=profile.node)

# Detail Views
class RegistryDetailView(generics.RetrieveAPIView):
    """
    Registry Entry details.
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (DjangoModelPermissions,)
    serializer_class = RegistryEntrySerializer
    model = RegistryEntry
    lookup_field = "dpn_object_id"


class NodeDetailView(generics.RetrieveUpdateAPIView):
    """
    Node details.
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (DjangoModelPermissions,)
    model = Node
    serializer_class = NodeSerializer
    lookup_field = "namespace"

class TransferDetailView(generics.RetrieveUpdateAPIView):
    """
    Details about a specific Transfer Action.
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (DjangoModelPermissions, IsNodeUser)
    lookup_field = "event_id"
    model = Transfer
    serializer_class = TransferSerializer

# # services views
# class RestoreView(generics.APIView):
#     pass