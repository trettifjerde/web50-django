import json
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import HttpResponse, render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import User, Email

def ajax_and_authenticated(function):
    def wrapper(request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if request.user.is_authenticated:
                return function(request, *args, **kwargs)
            else:
                return JsonResponse({"error": "Not authenticated"}, status=401)
        else: 
            return redirect(reverse("home:login") + '?next=/mailNg/', **kwargs)
    return wrapper

def getEmails(request, mailbox):
    if mailbox == "inbox":
        emails = Email.objects.filter(
            user=request.user, recipients=request.user, archived=False
        )
    elif mailbox == "sent":
        emails = Email.objects.filter(
            user=request.user, sender=request.user
        )
    elif mailbox == "archived":
        emails = Email.objects.filter(
            user=request.user, recipients=request.user, archived=True
        )
    else:
        return ({"message": "Invalid mailbox."}, 400)

    # Return emails in reverse chronologial order
    emails = emails.order_by("-timestamp").all()
    return ([email.serialize() for email in emails], 200)


def index(request):
    # Authenticated users view their inbox
    if request.user.is_authenticated:
        return render(request, "mailNg/layout.html")

    # Everyone else is prompted to sign in
    else:
        return redirect(reverse("home:login") + '?next=/mailNg/')


@csrf_exempt
@ajax_and_authenticated
def compose(request):

    # Composing a new email must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Check recipient emails
    data = json.loads(request.body)
    usernames = [username.strip() for username in data.get("recipients").split(",")]
    if usernames == [""]:
        return JsonResponse({
            "error": "At least one recipient required."
        }, status=400)

    # Convert email addresses to users
    recipients = []
    for username in usernames:
        try:
            user = User.objects.get(username=username)
            recipients.append(user)
        except User.DoesNotExist:
            return JsonResponse({
                "error": f"User with username {username} does not exist."
            }, status=400)

    # Get contents of email
    subject = data.get("subject", "")
    body = data.get("body", "")

    # Create one email for each recipient, plus sender
    users = set()
    users.add(request.user)
    users.update(recipients)
    for user in users:
        email = Email(
            user=user,
            sender=request.user,
            subject=subject,
            body=body,
            read=user == request.user
        )
        email.save()
        for recipient in recipients:
            email.recipients.add(recipient)
        email.save()

    emails, status = getEmails(request, 'sent')
    return JsonResponse(emails, status=status, safe=False)


@ajax_and_authenticated
def mailbox(request, mailbox):

    # Filter emails returned based on mailbox
    emails, status = getEmails(request, mailbox)
    return JsonResponse(emails, status=status, safe=False)

@csrf_exempt
@ajax_and_authenticated
def email(request, email_id):

    # Query for requested email
    try:
        email = Email.objects.get(user=request.user, pk=email_id)
    except Email.DoesNotExist:
        return JsonResponse({"error": "Email not found."}, status=404)

    # Return email contents
    if request.method == "GET":
        return JsonResponse(email.serialize())

    # Update whether email is read or should be archived
    elif request.method == "PUT":
        data = json.loads(request.body)
        if data.get("read") is not None:
            email.read = data["read"]
            email.save()
        if data.get("archived") is not None:
            email.archived = data["archived"]
            email.save()
            return JsonResponse({}, status=200)
        return HttpResponse(status=204)

    # Email must be via GET or PUT
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)

@csrf_exempt
@ajax_and_authenticated
def delete(request):
    if request.method == "POST":
        try:
            email_id = json.loads(request.body)['id']
            email = Email.objects.get(pk=email_id)
            email.delete()
            return JsonResponse({})
        except:
            return JsonResponse({}, status=400)

@ajax_and_authenticated
def setUsername(request):
    return JsonResponse({'username': request.user.username}, status=200)