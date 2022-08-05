document.addEventListener("DOMContentLoaded", function () {
	// Use buttons to toggle between views
	document.querySelector("#inbox").addEventListener("click", () => load_mailbox("inbox"));
	document.querySelector("#sent").addEventListener("click", () => load_mailbox("sent"));
	document.querySelector("#archived").addEventListener("click", () => load_mailbox("archive"));
	document.querySelector("#compose").addEventListener("click", compose_email.bind(null, null));

	// By default, load the inbox
	load_mailbox("inbox");
});

function compose_email(reply) {
	// Show compose view and hide other views
	document.querySelector("#email-view").style.display = "none";
	document.querySelector("#emails-view").style.display = "none";
	document.querySelector("#compose-view").style.display = "block";
	document.querySelector("#compose-view button").addEventListener("click", sendEmail);

	// Clear out composition fields
	document.querySelector("#compose-recipients").value = "";
	document.querySelector("#compose-subject").value = "";
	document.querySelector("#compose-body").value = "";

  if (reply)
  {
    document.querySelector("#compose-recipients").value = reply.sender;
    document.querySelector("#compose-subject").value = reply.subject;
    document.querySelector("#compose-body").value = reply.body;
    document.querySelector("#compose-body").selectionEnd = 0;
    document.querySelector("#compose-body").focus();
  }
}

function load_mailbox(mailbox) {
  
	function getRecipients(email) {
		if (email.recipients.length > 1)
			return `${email.recipients[0]} <span class="extra-recip">+${
				email.recipients.length - 1
			}</span>`;
		else return email.recipients[0];
	}

  function appendArchiveBtn(entry, email, btnText) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.innerHTML = btnText;
    btn.className = 'btn archive';
    btn.addEventListener('click', (e) => { 
      e.stopPropagation();
      e.target.disabled = true;

      fetch(`/mail/emails/${email.id}`, {
        method: 'PUT',
        body: JSON.stringify({
          archived: !(email.archived)
        })
      })
      .then(response => { response.status === 204 ? load_mailbox('inbox') : console.log(response)})
      .catch(err => console.log(err));
    });
    entry.querySelector('.timestamp').append(btn);
  }

	const emailList = document.querySelector('#emails-view div');

	document.querySelector("#emails-view h3").innerHTML = `${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}`;
	emailList.innerHTML = "Loading...";

	fetch(`/mail/emails/${mailbox}`)
		.then(response => response.json())
		.then(data => {
			if (data.length > 0) {

				emailList.innerHTML = "";
        let fillSender;
        let processArchiveBtn;
        
        switch(mailbox) {
          case 'sent':
            processArchiveBtn = () => {};
            fillSender = (email) => getRecipients(email);
            break;
          case 'archive':
            processArchiveBtn = (entry, email) => appendArchiveBtn(entry, email, 'Unarchive');
            fillSender = (email) => { return email.sender };
            break;
          case 'inbox':
            processArchiveBtn = (entry, email) => appendArchiveBtn(entry, email, 'Archive');
            fillSender = (email) => { return email.sender };   
            break;
        }

				data.forEach(email => {
					const entry = document.createElement("div");
					entry.innerHTML = `<div><span class="sender">${fillSender(email)}</span><span>${email.subject}</span></div>`;
					entry.innerHTML += `<div class="timestamp">${email.timestamp}</div>`;
          processArchiveBtn(entry, email);
					entry.className = `entry ${email.read ? "read" : ""}`;
					entry.addEventListener("click", () => openEmail(email.id));

					emailList.append(entry);
				});
			} 
      else 
        emailList.innerHTML = "No emails yet.";
		})
		.catch(err => {
			console.log(err);
			emailList.innerHTML =
				"Error loading emails. Check your Internet connection";
		});

	// Show the mailbox and hide other views
	document.querySelector("#emails-view").style.display = "block";
	document.querySelector("#compose-view").style.display = "none";
	document.querySelector("#email-view").style.display = "none";
}

function openEmail(id) {
	fetch(`/mail/emails/${id}`)
		.then(response => response.json())
		.then(data => {
			document.querySelector("#email-from").innerHTML = data.sender;
			document.querySelector("#email-to").innerHTML = data.recipients.join(", ");
			document.querySelector("#email-subject").innerHTML = data.subject;
			document.querySelector("#email-date").innerHTML = data.timestamp;
			document.querySelector("#email-header").style.display = "block";
			document.querySelector("#email-body").innerHTML = data.body.replaceAll('\n', '<br>');

      document.querySelector('#email-header button').addEventListener('click', compose_email.bind(null, {
        sender: data.sender,
        subject: 'Re: ' + data.subject,
        body: `\n---\n${data.sender} (${data.timestamp}):\n\n"${data.body}"`
      }));

			if (data.read === false) {
				fetch(`/mail/emails/${id}`, {
					method: "PUT",
					body: JSON.stringify({ read: true }),
				}).catch((err) => console.log(err));
			}
		})
		.catch((err) => {
			console.log(err);
			document.querySelector("#email-body").innerHTML =
				"Error loading email. Check your Internet connection";
		});

  document.querySelector("#emails-view").style.display = "none";
  document.querySelector("#compose-view").style.display = "none";
	document.querySelector("#email-header").style.display = "none";
	document.querySelector("#email-body").innerHTML = "Loading...";
	document.querySelector("#email-view").style.display = "block";
}

function sendEmail() {
	const form = this.form;

	fetch("/mail/emails/", {
		method: "POST",
		body: JSON.stringify({
			recipients: form["compose-recipients"].value,
			subject: form["compose-subject"].value,
			body: form["compose-body"].value,
		}),
	})
		.then(response => response.json())
		.then(result => {
			if ("error" in result)
				displayFormError(form, form["compose-recipients"], result.error);
			else 
        load_mailbox("sent");
		})
		.catch((err) => console.log(err));
}

function displayFormError(form, element, message) {
	const errorDiv = form.querySelector(".error-msg");
	errorDiv.innerHTML = message;
	element.classList.add("error");
	element.scrollIntoView({behavior: 'smooth'});
}