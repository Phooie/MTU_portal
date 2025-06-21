from django.shortcuts import render 
from elasticsearch_dsl.query import MultiMatch, Q
from .documents import ResourceDocument

def search(request):
    q = request.GET.get("q")
    context = {}
    if q:
        query = MultiMatch(query=q, fields=["title", "instructor","description"], fuzziness="AUTO")
        s = ResourceDocument.search().query(query)
        context ["resource"] = s
    return render (request, "search.html", context)