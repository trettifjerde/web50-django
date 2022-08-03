from django.shortcuts import render, redirect
from random import choice

from . import util
from .forms import NewEntry

def index(request):
    return render(request, "wiki/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    entry = util.get_entry(title)
    if entry:
        return render(request, "wiki/entry.html", {'title': title, 'entry': entry})
    else:
        return redirect("wiki:404", title=title)

def search(request):
    if request.method == 'POST':
        q = request.POST['q']
        if q and util.entry_exists(q):
            return redirect("wiki:entry", title=q)
        return render(request, "wiki/404.html", {'title': q, 'entries': [name for name in util.list_entries() if q.lower() in name.lower()]})
    return redirect('wiki:index')

def new(request):
    if request.method == "POST":
        form = NewEntry(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]

            if util.entry_exists(title):
                return render(request, "wiki/exists.html", {'title': title})

            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return redirect("wiki:entry", title=title)
        else:
            return render(request, "wiki/form.html", {'form': form})
    return render(request, "wiki/form.html", {'form': NewEntry()})

def edit(request, title):
    if request.method == "POST":
        if util.entry_exists(title):
            form = NewEntry({"title": title, "content": request.POST["content"]})
            if form.is_valid():
                util.save_entry(title, form.cleaned_data["content"])
                return redirect("wiki:entry", title=title)
            else:
                context["form"] = form
                return render(request, "wiki/form.html", {"form": form})
        else:
            return redirect("wiki:404", title=title)

    entry = util.get_entry(title)
    if entry:
        return render(request, "wiki/form.html", {"form": NewEntry({'title': title, 'content': entry})})
    else:
        return redirect('wiki:404', title=title)

def random(request):
    title = choice(util.list_entries())
    return redirect("wiki:entry", title=title)

def delete(request, title):
    if util.delete_entry(title):
        return redirect("wiki:index")
    return redirect('wiki:404', title=title)

def not_found(request, title):
    return render(request, "wiki/404.html", {"title": title})