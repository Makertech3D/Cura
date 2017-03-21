# Copyright (c) 2017 Ultimaker B.V.
# Cura is released under the terms of the AGPLv3 or higher.

from UM.MimeTypeDatabase import MimeType, MimeTypeDatabase
from UM.Settings.ContainerStack import ContainerStack
from UM.Settings.ContainerRegistry import ContainerRegistry

class CannotSetNextStackError(Exception):
    pass

class GlobalStack(ContainerStack):
    def __init__(self, container_id, *args, **kwargs):
        super().__init__(container_id, *args, **kwargs)

    def getProperty(self, key, property_name):

    @pyqtProperty(InstanceContainer)
    def userChanges(self) -> InstanceContainer:
        return self._containers[_ContainerIndexes.UserChanges]

    @pyqtProperty(InstanceContainer)
    def qualityChanges(self) -> InstanceContainer:
        return self._containers[_ContainerIndexes.QualityChanges]

    @pyqtProperty(InstanceContainer)
    def quality(self) -> InstanceContainer:
        return self._containers[_ContainerIndexes.Quality]

    @pyqtProperty(InstanceContainer)
    def material(self) -> InstanceContainer:
        return self._containers[_ContainerIndexes.Material]

    @pyqtProperty(InstanceContainer)
    def variant(self) -> InstanceContainer:
        return self._containers[_ContainerIndexes.Variant]

    @pyqtProperty(InstanceContainer)
    def definitionChanges(self) -> InstanceContainer:
        return self._containers[_ContainerIndexes.DefinitionChanges]

    @pyqtProperty(DefinitionContainer)
    def definition(self) -> DefinitionContainer:
        return self._containers[_ContainerIndexes.Definition]

        if property_name == "value":
            resolve = super().getProperty(key, "resolve")
            if resolve:
                return resolve

        return super().getProperty(key, property_name)

    def setNextStack(self, next_stack):
        raise CannotSetNextStackError("Global stack cannot have a next stack!")

    ##  Overridden from ContainerStack
    @override(ContainerStack)
    def deserialize(self, contents: str) -> None:
        super().deserialize(contents)

        new_containers = self._containers.copy()
        while(len(new_containers) < len(_ContainerIndexes.IndexTypeMap)):
            new_containers.append(self._empty_instance_container)

        # Validate and ensure the list of containers matches with what we expect
        for index, type_name in _ContainerIndexes.IndexTypeMap.items():
            try:
                container = new_containers[index]
            except IndexError:
                container = None

            if type_name == "definition":
                if not container or not isinstance(container, DefinitionContainer):
                    definition = self.findContainer(container_type = DefinitionContainer, category = "*")
                    if not definition:
                        raise InvalidContainerStackError("Stack {id} does not have a definition!".format(id = self._id))

                    new_containers[index] = definition
                continue

            if not container or container.getMetaDataEntry("type") != type_name:
                actual_container = self.findContainer(type = type_name)
                if actual_container:
                    new_containers[index] = actual_container

        self._containers = new_containers

## private:

global_stack_mime = MimeType(
    name = "application/x-cura-globalstack",
    comment = "Cura Global Stack",
    suffixes = [ "global.cfg" ]
)

MimeTypeDatabase.addMimeType(global_stack_mime)
ContainerRegistry.addContainerTypeByName(GlobalStack, "global_stack", global_stack_mime.name)

class _ContainerIndexes:
    UserChanges = 0
    QualityChanges = 1
    Quality = 2
    Material = 3
    Variant = 4
    DefinitionChanges = 5
    Definition = 6

    # Simple hash map to map from index to "type" metadata entry
    IndexTypeMap = {
        UserChanges: "user",
        QualityChanges: "quality_changes",
        Quality: "quality",
        Material: "material",
        Variant: "variant",
        DefinitionChanges: "definition_changes",
        Definition: "definition",
    }
