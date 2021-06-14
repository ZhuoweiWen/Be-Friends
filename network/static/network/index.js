var pos_com = 0; //Global variable
var re_comment = false; //Global variable

document.addEventListener('DOMContentLoaded', () => {

    document.querySelector('input[value=Submit]').addEventListener('click', new_post);  
    document.querySelectorAll('input[value=Edit]').forEach
    (element => element.addEventListener('click', event => {
      display_edit_form(event);
    }));
    document.querySelectorAll('input[value="Leave a comment"]').forEach
    (element => element.addEventListener('click', event => {
      display_comment_form(event);
    }));
    document.querySelectorAll('input[value=Reply]').forEach
    (element => element.addEventListener('click', event => {
      display_nested_comment_form(event);
    }));
    document.querySelectorAll('input[value=Comments]').forEach
    (element => element.addEventListener('click', event => {
      display_comments(event);
    }));
    document.querySelectorAll('input[value=Save]').forEach
    (element => element.addEventListener('click', event => {
      event.preventDefault();
      edit(event);
    }));
    document.querySelectorAll('input[value=Post]').forEach
    (element => element.addEventListener('click', event => {
      event.preventDefault();
      comment(event);
    }));
    document.querySelectorAll('.fa-heart-o').forEach(
      element => element.addEventListener('click', event => {
      event.preventDefault();
      like(event);
    }))
    document.querySelectorAll('.fa-heart').forEach(
      element => element.addEventListener('click', event => {
      event.preventDefault();
      like(event);
    }))
});


function new_post() {


  const content = document.querySelector('#post-body').value;
    

  const csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value
  const request = new Request(
    '/posts',
    {headers: {'X-CSRFToken': csrftoken}}
  );

  fetch(request, {
      method: 'POST',
      body: JSON.stringify({
         content: content,
         
      })
  })
    .then(response => response.json())
    .then(result => {

        console.log(result);

        create_message(result);

      
  })
}

function display_edit_form(event) {
  const clicked = event.target.parentElement.parentElement.parentElement;

  clicked.children[0].style.display = 'none';
  clicked.children[3].style.display = 'none';
  clicked.children[1].style.display = 'block';
}

function display_comment_form(event) {
  const clicked = event.target.parentElement.parentElement.parentElement;
  clicked.children[2].children[0].value = '';
  clicked.children[3].style.display = 'block';
  clicked.children[2].style.display = 'block';
  pos_com = 0;
  re_comment = false;
}

function display_comments(event){
  const clicked = event.target.parentElement.parentElement.parentElement;
  clicked.children[3].style.display = 'block';
}

function display_nested_comment_form(event){
  const clicked = event.target.parentElement.parentElement.parentElement.parentElement;
  const forloop_count = parseInt(event.target.parentElement.parentElement.dataset.commentno);
  const content = clicked.children[3].children[forloop_count].children[1].innerText;
  const date = clicked.children[3].children[forloop_count].children[2].innerHTML.split('<')[0].trim();
  const concated =  `
                      
                      Re: ${content} ${date}`;

  clicked.children[2].children[0].value = concated;  
  clicked.children[3].style.display = 'block';
  clicked.children[2].style.display = 'block';
  pos_com = forloop_count;
  re_comment=true;
}



//To do: implement put edit method
function edit(event) {
  const clicked = event.target.parentElement;
  const content = clicked.children[0].value;
  const post_id = clicked.parentElement.dataset.id;

  const csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value
  const request = new Request(
    '/edit',
    { headers: { 'X-CSRFToken': csrftoken } }
  );

  fetch(request, {
    method: 'PUT',
    body: JSON.stringify({
      index: post_id,
      content: content      
    })
  })
    .then(response => response.json())
    .then(result => {

      console.log(result);

      create_message(result);
      


    })
}

function like(event){
  const clicked = event.target;
  const post_id = clicked.parentElement.parentElement.parentElement.dataset.id;
  var like_count = parseInt(clicked.innerHTML);

  const csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value
  const request = new Request(
    '/like',
    { headers: { 'X-CSRFToken': csrftoken } }
  );

  fetch(request, {
    method: 'PUT',
    body: JSON.stringify({
      index:post_id
    })
  })
  .then(response => response.json())
  .then(result => {
    console.log(result);
    const parsed = JSON.parse(JSON.stringify(result));
    if (parsed.message === "Unliked post."){
      like_count--;
      clicked.innerHTML= ` ${like_count}`;
      toggle(clicked, false);
    }
    else if(parsed.message === "Liked post."){
      like_count++;
      clicked.innerHTML= ` ${like_count}`;
      toggle(clicked, true);
    }
  })

}

function comment(event) {
  const clicked = event.target.parentElement;
  const content = clicked.children[0].value;
  const post_id = clicked.parentElement.dataset.id;

  var parsed_post = '';
  var comment_id = 0;


  if (re_comment){
    parsed_post = content.split('Re:')[0].trim();
    comment_id = parseInt(event.target.parentElement.parentElement.
                          children[3].children[pos_com].children[2].children[0].dataset.commentid);
  }
  else {
    parsed_post = content;
  }
  const csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value

  const request = new Request(
    '/comment',
    { headers: { 'X-CSRFToken': csrftoken } }
  );

  console.log(parsed_post)
  console.log(comment_id)
  console.log(post_id)
  console.log(re_comment)
  fetch(request, {
    method: 'POST',
    body: JSON.stringify({
      post_id: post_id,
      content: parsed_post,
      comment_id: comment_id,
      re_comment: re_comment      
    })
  })
  .then(response => response.json())
  .then(result => {
    console.log(result);
    create_message(result);
  })
}

function create_message(result){
  //Clear all the message in message view
  document.querySelector('#message-view').innerHTML = '';

  //Create and style message item
  const message = document.createElement('p');
  message.style.padding = '10px';
  message.style.paddingLeft = '20px';
  message.style.borderRadius = '10px';

  if (result['message']) {
    //Add returned message to message item
    message.innerHTML = result['message'];
    message.style.backgroundColor = 'rgb(176, 225, 255)';
    //Manual redirect so the address wouldn't have csrf token
    window.location.href = '';


  }
  else {
    //Add returned error to message item
    message.innerHTML = result['error'];
    message.style.backgroundColor = 'rgb(255, 188, 176)';

  }

  //Add message item to message view
  document.querySelector('#message-view').append(message);
  document.querySelector('#message-view').style.display = 'block';
}

//@param like the boolean to determine the user is liking or unliking
function toggle(clicked, like){
  if (like) {
    clicked.classList.remove('fa-heart-o');
    clicked.classList.add('fa-heart');
  }
  else {
    clicked.classList.remove('fa-heart');
    clicked.classList.add('fa-heart-o');
  }
}

