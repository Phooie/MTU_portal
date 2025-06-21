from django_elasticsearch_dsl import Document 
from django_elasticsearch_dsl.registries import registry
from . books import Resource

@registry.register_document 

class ResourceDocument(Document):
    class Index:
        name= "resource"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Resource
        fields = ["title","instructor",'description','link','resource_type','category']



from .books import News  # Import your News model

@registry.register_document
class NewsDocument(Document):
    class Index:
        name = "news_index"  # Name of the Elasticsearch index
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = News
        fields = [
            "title",
            "description",
            "link",
            "start_date",
            "end_date",
            "category",
            "posted_by",
            "is_new"
        ]


from .books import Course_table,Books_table

@registry.register_document
class CourseDocument(Document):
    class Index:
        name = "course_index"  # Name of the Elasticsearch index
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Course_table
        fields = ["title", "instructor", "description", "category", "link"]




@registry.register_document
class BookDocument(Document):
    class Index:
        name = "book_index"  # Name of the Elasticsearch index
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Books_table
        fields = ["title", "author", "description", "category", "link"]


from .books import Research

@registry.register_document
class ResearchDocument(Document):
    class Index:
        name = "research_index"  # Name of the Elasticsearch index
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Research
        fields = ["title", "researcher", "abstract", "category", "document_link"]


