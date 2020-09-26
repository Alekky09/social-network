if(document.getElementById("follow")){
    document.getElementById("follow").addEventListener("click", function(){
        fetch(window.location.href, {
            method: "PUT",
            headers: { "X-CSRFToken": csrftoken }
        })
        .then(response => response.json())
        .then(data => {
            this.innerText = data.follow;
            document.getElementById("followers").innerText = data.followers;
            document.getElementById("following").innerText = data.following
        })
    })
}
document.querySelectorAll("ion-icon").forEach(function(icon) {
    icon.addEventListener("click", function(){
        fetch(window.location.href, {
            method: "PUT",
            body: JSON.stringify({
                post_id: this.closest('.post').id}),
            headers: { "X-CSRFToken": csrftoken }
        })
        .then(response => response.json())
        .then(data => {
            if(data.like){
                this.setAttribute("name", "heart")
            }
            else{
                this.setAttribute("name", "heart-outline")
            }
            this.previousElementSibling.innerText = data.likescount;
        })
    })
})

function edit(button){
    var text = button.parentElement.nextElementSibling;
    
    if(text.style.display === "none"){
        button.innerText = "Edit";
        text.nextElementSibling.setAttribute("hidden", true);
        text.removeAttribute("style");
        button.nextElementSibling.setAttribute("hidden", true);
    }
    else{
        button.innerText = "Close";
        text.style.display = "none";
        text.nextElementSibling.removeAttribute("hidden");
        button.nextElementSibling.removeAttribute("hidden");
    }
}

function saveEdit(button){
    var text = button.parentElement.nextElementSibling;
    fetch(window.location.href, {
        method: "PUT",
        body: JSON.stringify({
            post_id: button.closest('.post').id,
            post_content: text.nextElementSibling.value}),
        headers: { "X-CSRFToken": csrftoken }
    })
    .then(response => response.json())
    .then(data => {
        if(data.success){
            text.innerText = data.content;
            text.nextElementSibling.setAttribute("hidden", true);
            text.removeAttribute("style");
            button.previousElementSibling.innerText = "Edit";
            button.setAttribute("hidden", true);
        }
    })
}

function validateForm(){
    var post = document.forms["newpostform"]["newpost"].value.trim();
    if(post == null || post == ""){
        document.forms["newpostform"]["newpost"].value = "";
        return false;
    }
}