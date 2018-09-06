"""Resolwe relation serializer."""
from django.db import transaction

from rest_framework import serializers

from resolwe.flow.models.collection import Collection
from resolwe.flow.models.entity import Relation, RelationPartition, RelationType
from resolwe.rest.serializers import SelectiveFieldMixin

from .base import ResolweBaseSerializer


class RelationPartitionSerializer(SelectiveFieldMixin, serializers.ModelSerializer):
    """Serializer for RelationPartition objects."""

    class Meta:
        """RelationPartitionSerializer Meta options."""

        model = RelationPartition
        fields = ('id', 'entity', 'position', 'label')


class RelationSerializer(ResolweBaseSerializer):
    """Serializer for Relation objects."""

    partitions = RelationPartitionSerializer(source='relationpartition_set', many=True)
    collection = serializers.PrimaryKeyRelatedField(queryset=Collection.objects.all())

    class Meta:
        """RelationSerializer Meta options."""

        model = Relation
        read_only_fields = (
            'created',
            'id',
            'modified',
        )
        update_protected_fields = (
            'contributor',
            'type',
        )
        fields = read_only_fields + update_protected_fields + (
            'collection',
            'category',
            'partitions',
            'unit',
        )

    def get_fields(self):
        """Dynamically adapt fields based on the current request."""
        fields = super(RelationSerializer, self).get_fields()

        if self.request.method == "GET":
            fields['type'] = serializers.CharField(source='type.name')
        else:
            fields['type'] = serializers.PrimaryKeyRelatedField(queryset=RelationType.objects.all())

        return fields

    def _create_partitions(self, instance, partitions):
        """Create partitions."""
        for partition in partitions:
            RelationPartition.objects.create(
                relation=instance,
                entity=partition['entity'],
                label=partition.get('label', None),
                position=partition.get('position', None),
            )

    def create(self, validated_data):
        """Create ``Relation`` object and add partitions of ``Entities``."""
        # `partitions` field is renamed to `relationpartition_set` based on source of nested serializer
        partitions = validated_data.pop('relationpartition_set', {})

        with transaction.atomic():
            instance = Relation.objects.create(**validated_data)
            self._create_partitions(instance, partitions)

        return instance

    def update(self, instance, validated_data):
        """Update ``Relation``."""
        # `partitions` field is renamed to `relationpartition_set` based on source of nested serializer
        partitions = validated_data.pop('relationpartition_set', {})

        with transaction.atomic():
            instance = super().update(instance, validated_data)

            # TODO: Apply the diff instead of recreating all obejcts.
            instance.relationpartition_set.all().delete()
            self._create_partitions(instance, partitions)

        return instance