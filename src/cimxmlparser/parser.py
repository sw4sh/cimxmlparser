# @author: Segrenev Mikhail, 2023

import xml.etree.ElementTree as ET
import pathlib
import uuid

from .xtramvlib import *

rdf_uri = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] - %(message)s')


class XMLMapObject:

    def __init__(self, class_name: str, namespace: str, method: str):
        self.class_name = class_name
        self.namespace = namespace
        if method not in ["TEXT", "ATTRIBUTE"]:
            raise Exception(f"Указан неверный параметр -> method.")
        else:
            self.method = method
        self.dictionary = None

    @property
    def value(self):
        return {self.class_name: {
            "namespace": self.namespace,
            "method": self.method}}


class XMLMap:
    DEFAULT_LIBRARY_PATH = pathlib.Path(pathlib.Path.cwd(), "CIMXML.library")

    def __init__(self, from_library: str = None, from_dictionary: dict = None):
        self.map = dict()
        self.objects = list()
        if from_library is not None and from_dictionary is None:
            self.loadFromLibraryFile(from_library)
        elif from_library is None and from_dictionary is not None:
            self.set(from_dictionary)
            for class_name, values in from_dictionary.items():
                self.objects.append(XMLMapObject(class_name, values.get("namespace"), values.get("method")))
        else:
            raise Exception(f"Критическая ошибка инициализации объекта.")

    def get(self):
        if self.map is not None:
            return self.map
        else:
            raise Exception(f"Отсутствует XMLMap")

    def set(self, xmlmap: dict):
        self.map = xmlmap

    def update(self, xmlmap_object: XMLMapObject):
        try:
            self.objects.append(xmlmap_object)
            self.map.update(xmlmap_object.value)
        except Exception as excp:
            raise Exception(f"Обнаружена критическая ошибка во время обновления XMLMap -> {excp}")

    def createXMLLibrary(self, xml_file_path: str):
        TimeCounter = PerfomanceTimeCounter()
        try:
            xml_obj_list = xmllibrarygenerator(xml_file_path)
        except Exception as excp:
            raise Exception(f"Обнаружена критическая ошибка во время создания XMLLibrary -> {excp}")
        self.objects = xml_obj_list
        del xml_obj_list
        logging.info(
            f"Файл XMLLibrary успешно сформирован за {TimeCounter.elapsedTime()}")

    def saveToLibraryFile(self, library_path: str = DEFAULT_LIBRARY_PATH):
        with open(library_path, mode="w", encoding="UTF-8") as library_file:
            for obj in self.objects:
                library_file.writelines(f"{obj.class_name}||{obj.namespace}||{obj.method}\n")

    def loadFromLibraryFile(self, xml_library: str = None):
        if xml_library is not None and ".library" not in xml_library:
            raise Exception(f"Выбран некорректный файл XMLLibrary.")
        elif xml_library is not None and ".library" in xml_library:
            with open(xml_library, mode="r", encoding="UTF-8") as xml_library_file:
                xml_library_data = xml_library_file.readlines()
                xml_library_file.close()
            for xmlmap_object in xml_library_data:
                props = xmlmap_object.split('||')
                self.map.update({props[0]: {
                    "namespace": props[1],
                    "method": props[2].strip()
                }})

    def unpackXMLMapObjects(self):
        for obj in self.objects:
            self.map.update({obj.class_name: {
                "namespace": obj.namespace,
                "method": obj.method
            }})


class CIMXMLParser:
    STABLE_VERSION = "STABLE"
    LM_VERSION = "ALPHA"
    LXML_ET_VERSION = "LXML_ETREE"
    versions = [STABLE_VERSION, LM_VERSION, LXML_ET_VERSION]
    DEFAULT_OUTPUT_PATH = pathlib.Path(pathlib.Path.cwd(), "CIMXMLParserWriteResult.xml")

    def __init__(self, version: str = STABLE_VERSION, _xmlmap: dict = None):
        if version not in self.versions:
            raise Exception("Указана неверная версия Парсера.\nСм. CIMXMLParser.versions для доступных вариантов.")
        self.version = version
        self._parsed_data = None
        if _xmlmap is not None:
            self.xmlmap = XMLMap(from_dictionary=_xmlmap)
        else:
            self.xmlmap = None

    def parseFile(self, filepath: str, log_level: str = "main"):
        """
        Выполнить парсинг файла расширения .xml
        :param filepath: Путь до файла для парсинга (pathlib.Path)
        :param log_level: Уровень логгирования
            all - Полное логгирование (Самое медленное);
            main - Только основные объекты (Сбалансированное);
            null - Не выводить информации об обработанных объектах.
        """
        TimeCounter = PerfomanceTimeCounter()
        logging.warning(f"#VERSION={self.version}  #LOG_LEVEL={log_level}")
        if ".xml" not in filepath:
            raise Exception("Парсинг может осуществляться только для файла с расширением .xml")
        match self.version:
            case "STABLE":
                try:
                    self._parsed_data, _xmlmap = parse(filepath, log_level)
                    self.xmlmap = XMLMap(from_dictionary=_xmlmap)
                except Exception as excp:
                    self._parsed_data = None
                    raise Exception(f"Критическая ошибка при выполнении парсинга. -> {excp}")
            case "ALPHA":
                try:
                    raise Exception(f"Версия {self.version} не поддерживается")
                except Exception as excp:
                    self._parsed_data = None
                    raise Exception(f"Критическая ошибка при выполнении парсинга. -> {excp}")
            case "LXML_ETREE":
                try:
                    raise Exception(f"Версия {self.version} не поддерживается")
                except Exception as excp:
                    self._parsed_data = None
                    raise Exception(f"Критическая ошибка при выполнении парсинга. -> {excp}")
            case _:
                raise Exception(f"Ошибка инициализации Парсера версии {self.version}.")
        logging.info(
            f'Выполнен парсинг файла {filepath}. Время выполнения: {TimeCounter.elapsedTime()}')

    def writeToCIMXML(
            self, xmlmap: XMLMap = None, parsed_data: dict = None, output_file: str = DEFAULT_OUTPUT_PATH):
        TimeCounter = PerfomanceTimeCounter()
        if parsed_data is None:
            parsed_data = self._parsed_data
        if xmlmap is not None:
            self.xmlmap = xmlmap

        try:
            write_to_xml(parsed_data, self.xmlmap.get(), output_file)
        except Exception as excp:
            raise Exception(f"Возникла критическая ошибка во время записи XML-файла -> {excp}")
        logging.info(f"Выполнена запись CIMXML-файла по пути: {output_file}. Время выполнения: {TimeCounter.elapsedTime()}")

    def to_dictionary(self):
        if self._parsed_data is None:
            raise Exception(f"Нет обработанных данных!")
        else:
            return self._parsed_data

    def updateCIMObject(self, object_class: str, object_uuid: str, changable_object_property: str,
                        object_property_new_value: list, create_property: bool = False):
        if self._parsed_data is None:
            raise Exception(f"Нет обработанных данных!")
        else:
            if self._parsed_data.get(object_class) is None:
                raise Exception(f"В объекте данных не существует класса '{object_class}'")
            if self._parsed_data.get(object_class).get(object_uuid) is None:
                raise Exception(f"В объекте данных не существует объекта класса '{object_class}' и UUID = '{object_uuid}'")
            if self._parsed_data.get(object_class).get(object_uuid).get(changable_object_property) is None and create_property is False:
                raise Exception(f"У объекта класса '{object_class}, UUID = '{object_uuid}' не существует свойства '{changable_object_property}''")
            try:
                self._parsed_data[object_class][object_uuid][changable_object_property] = object_property_new_value
            except Exception as excp:
                raise Exception(f"Критическая ошибка обновления данных! -> {excp}")

    def updateCIMObjects(self, object_class_uuid_pair_list: list, changable_object_property: str,
                         object_property_new_value: list, create_property: bool = False):
        update_cim_objects_exceptions = list()
        update_counter = int()
        for object_class_uuid_pair in object_class_uuid_pair_list:
            if type(object_class_uuid_pair) is not tuple:
                raise Exception(f"Неверно передана структура списка объектов для объекта '{object_class_uuid_pair}'"
                                f"Необходимая структура -> [(object_class, object_uuid)]'")
            else:
                object_class = object_class_uuid_pair[0]
                object_uuid = object_class_uuid_pair[1]
                try:
                    self.updateCIMObject(object_class, object_uuid, changable_object_property, object_property_new_value, create_property)
                    update_counter += 1
                except Exception as excp:
                    update_cim_objects_exceptions.append(f"Не удалось обновить объект '{object_class_uuid_pair}' -> {excp}\n")
        logging.info(f"Обновлено {update_counter} объектов из {len(object_class_uuid_pair_list)}.")
        if len(update_cim_objects_exceptions) != 0:
            logging.info(f"Ошибки при обновлении:")
            logging.info(''.join(update_cim_objects_exceptions))

    def createCIMObject(self, object_class: str, properties: dict,
                        object_uuid: str = None, overwrite_properties: bool = False):
        for key, value in properties.items():
            if type(value) is not list:
                raise Exception(f"Значение свойства [{key}] создаваемого объекта должно быть [list], а не [{type(value)}]!")

        if object_uuid is None:
            object_uuid = str(uuid.uuid4())
        else:
            if not is_uuid(object_uuid):
                raise Exception(f"Идентификатор объекта [{object_uuid}] не является uuid!")
        if self._parsed_data.get(object_class).get(object_uuid) is not None and overwrite_properties is False:
            raise Exception(f"Объект [{object_uuid}] класса [{object_class}] уже имеется в модели. "
                            f"Используйте overwrite_properties = True, чтобы перезаписать свойства объекта.")
        try:
            self._parsed_data[object_class][object_uuid] = properties
        except Exception as excp:
            raise Exception(f"Критическая ошибка создании объекта! -> {excp}")
        logging.info(f"Для класса [{object_class}] создан новый объект [{object_uuid}] "
                     f"с указанными свойствами [{properties}]")
        return object_uuid


def is_uuid(stroke: str):
    if type(stroke) != str:
        return False
    stroke = stroke.replace('#_', '')
    try:
        uuid.UUID(str(stroke))
        return True
    except ValueError:
        return False


def cimxmluuid_to_uuid(_uuid: str):
    return _uuid.replace('#_', '')


def uuid_to_cimxmluuid(_uuid: str):
    return f"#_{_uuid}"


def update_object_dictionary(key: str, value: str, object_dictionary: dict, log_level: str):
    if is_uuid(value):
        value = cimxmluuid_to_uuid(value)
    _is_key_in_object_dictionary = object_dictionary.get(key)
    if _is_key_in_object_dictionary is not None:
        key_value_object_dictionary = _is_key_in_object_dictionary
        key_value_object_dictionary.append(value)
        object_dictionary.update({key: key_value_object_dictionary})
    else:
        object_dictionary.update({
            key: [value]
        })
    if log_level == "all":
        logging.info(f"Для ключа '{key}' добавлено значение [{value}].")
    return object_dictionary


def parse(filepath: str, log_level: str = "main"):
    _xmlmap = dict()
    output_dictionary = dict()
    counter = 0

    xmltree = ET.parse(filepath)
    xmltree_root = xmltree.getroot()
    for obj in xmltree_root:
        object_dictionary = dict()
        object_class = obj.tag.split('}')[1]
        try:
            object_uuid = cimxmluuid_to_uuid(list(obj.attrib.values())[0])
        except IndexError:
            object_uuid = None
        object_namespace = obj.tag.split('}')[0].split('{')[1]
        if _xmlmap.get(object_class) is None:
            _xmlmap.update({object_class: {
                "namespace": object_namespace,
                "method": "ATTRIBUTE"
            }})

        if log_level != "null":
            logging.info(f"Найден новый объект класса [{object_class}], UUID: [{object_uuid}]")
        for child in obj:
            child_key = child.tag.split('}')[1]
            child_value = child.text
            child_namespace = child.tag.split('}')[0].split('{')[1]
            xmlmap_child_method = "TEXT"
            if child_value is None or len(child_value) == 0:
                try:
                    child_value = list(child.attrib.values())[0]
                    xmlmap_child_method = "ATTRIBUTE"
                except IndexError:
                    child_value = None
            object_dictionary = update_object_dictionary(child_key, child_value, object_dictionary, log_level=log_level)
            if _xmlmap.get(child_key) is None:
                _xmlmap.update({child_key: {
                    "namespace": child_namespace,
                    "method": xmlmap_child_method
                }})
        if output_dictionary.get(object_class) is None:
            output_dictionary.update({object_class: {}})
        output_dictionary[object_class][object_uuid] = object_dictionary
        counter += 1
    logging.info(f"Всего обработано {counter} объектов из файла.")
    return output_dictionary, _xmlmap


def write_to_xml(data_dictionary: dict, xmlmap: dict, output_file: str):
    tree = ET.ElementTree(ET.Element("{" + rdf_uri + "}" + "RDF"))
    root = tree.getroot()
    counter = int()
    for class_name, class_data in data_dictionary.items():
        for object_uuid, object_data in class_data.items():
            object_node = ET.Element(
                "{" + f"{xmlmap.get(class_name).get('namespace')}" + "}" + f"{class_name}")
            object_node.attrib = {str('{' + rdf_uri + '}' + 'about'): uuid_to_cimxmluuid(object_uuid)}

            for property_name, property_values in object_data.items():
                property_tag = "{" + f"{xmlmap.get(property_name).get('namespace')}" + "}" + f"{property_name}"
                for property_value in property_values:
                    if xmlmap.get(property_name).get('method') == "ATTRIBUTE":
                        property_attrib = {str('{' + rdf_uri + '}' + 'resource'): uuid_to_cimxmluuid(property_value)}
                        ET.SubElement(object_node, property_tag, property_attrib)
                    elif xmlmap.get(property_name).get('method') == "TEXT":
                        child_node = ET.Element(property_tag)
                        child_node.text = property_value
                        object_node.append(child_node)
                    else:
                        raise Exception(f"Невозможно определить метод записи [{xmlmap.get(property_name).get('method')}] "
                                        f"для свойства [{property_name}] со значением [{property_value}] "
                                        f"объекта [{object_uuid}]. Укажите корректный метод (ATTRIBUTE | TEXT).")
            root.append(object_node)
            counter += 1
    ET.indent(tree, space=" ", level=0)
    tree.write(output_file, xml_declaration=True, encoding='utf-8')


def xmllibrarygenerator(filepath: str):
    handled_classes = list()
    xmlLib = list()
    root = ET.iterparse(filepath, events=("start",))
    for event, obj in root:
        obj_names = obj.tag.split('}')
        obj_class_name = obj_names[1]

        if obj_class_name in handled_classes:
            continue

        obj_namespace = obj_names[0].split('{')[1]

        if obj.text is None or len(obj.text) == 0:
            obj_method = 'ATTRIBUTE'
        else:
            obj_method = 'TEXT'
        logging.info(f"Обработан Класс {obj_class_name}")
        xmlLib.append(XMLMapObject(class_name=obj_class_name, namespace=obj_namespace, method=obj_method))
        handled_classes.append(obj_class_name)
        del obj_names, obj_class_name, obj_namespace
    return xmlLib
