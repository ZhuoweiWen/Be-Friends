/* Script for handling action provided at all post page, including like,
    comments, edit post, and add new post */

//Global variable for comment_reply function so it can get the
//correct comment the user replys to
var pos_com = 0; 

//Global variable for comment, determine whether it is new comment or reply
var re_comment = false; 

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


//Function for adding new post
function new_post() {

  //Get content of user post
  const content = document.querySelector('#post-body').value;
 
  //Handle csrf token and request
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
        //Provide feedback
        create_message(result);

      
  })
} 

//Function for displaying the edit form
//@param event the current event
function display_edit_form(event) {
  //Get the div that contains the post
  const clicked = event.target.parentElement.parentElement.parentElement;
  //Hide post content and show edit form
  clicked.children[0].style.display = 'none';
  clicked.children[3].style.display = 'none';
  clicked.children[1].style.display = 'block';
}

//Function for displaying comment form
//@param event the current event
function display_comment_form(event) {
  //Get the div that contains the post
  const clicked = event.target.parentElement.parentElement.parentElement;
  //Get a empty textarea
  clicked.children[2].children[0].value = '';
  //Show comment form and comments
  clicked.children[3].style.display = 'block';
  clicked.children[2].style.display = 'block';
  //Update global variables, re_comment is false since it is not a reply
  pos_com = 0;
  re_comment = false;
}

//Function for displaying comments
//@param event the current event
function display_comments(event){
  //Get the div that contains the post
  const clicked = event.target.parentElement.parentElement.parentElement;
  //Show comments
  clicked.children[3].style.display = 'block';
}

//Function for replying comments
//@param event the current event
function display_nested_comment_form(event){
  //Get the div that contains the post
  const clicked = event.target.parentElement.parentElement.parentElement.parentElement;
  //Get the forloop_count from dataset, so it can get the correct comment content
  const forloop_count = parseInt(event.target.parentElement.parentElement.dataset.commentno);
  //Get the content of the comment the user is replying to
  const content = clicked.children[3].children[forloop_count].children[1].innerText;
  //Get the timestamp
  const date = clicked.children[3].children[forloop_count].children[2].innerHTML.split('<')[0].trim();

  //String for prepopulating the comment textarea
  const concated =  `
                      
                      Re: ${content} ${date}`;

  //Prepopulate and display the commment form
  clicked.children[2].children[0].value = concated;  
  clicked.children[3].style.display = 'block';
  clicked.children[2].style.display = 'block';
  //Update the global variables
  pos_com = forloop_count;
  re_comment=true;
}



//Edit function for editing post
//@param event the current event
function edit(event) {
  //Get the content of post and from parent element get the post_id from dataset
  const clicked = event.target.parentElement;
  const content = clicked.children[0].value;
  const post_id = clicked.parentElement.dataset.id;

  //Handle csrftoken and request
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
      //Update message-view to give feedback
      create_message(result);

    })
}

//Function for liking a post
//@param event the current event
function like(event){
  //Get the like count and post_id from dataset
  const clicked = event.target;
  const post_id = clicked.parentElement.parentElement.parentElement.dataset.id;
  var like_count = parseInt(clicked.innerHTML);

  //Handle csrf token and request
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
    //Parsed the result 
    const parsed = JSON.parse(JSON.stringify(result));

    if (parsed.message === "Unliked post."){
      //If unliked the post, update the count and make heart shape voided
      like_count--;
      clicked.innerHTML= ` ${like_count}`;
      toggle(clicked, false);
    }
    else if(parsed.message === "Liked post."){
      //If liked post, update the ocunt and make heart shape filled
      like_count++;
      clicked.innerHTML= ` ${like_count}`;
      toggle(clicked, true);
    }
  })

}

//Function for handling comment
//@param event the current event
function comment(event) {
  //Get the content of comment and post_id from dataset
  const clicked = event.target.parentElement;
  const content = clicked.children[0].value;
  const post_id = clicked.parentElement.dataset.id;

  //Create local variables
  var parsed_post = '';
  var comment_id = 0;

  
  if (re_comment){
    //If replying to comment, split and trim the comment so the
    //prepopulated content will be left out and update comment_id
    parsed_post = content.split('Re:')[0].trim();
    comment_id = parseInt(event.target.parentElement.parentElement.
                          children[3].children[pos_com].children[2].children[0].dataset.commentid);
  }
  else {
    //If new comment, get the content
    parsed_post = content;
  }

  //Handle csrf token and request
  const csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value
  const request = new Request(
    '/comment',
    { headers: { 'X-CSRFToken': csrftoken } }
  );

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
    //Provide feedback
    create_message(result);
  })
}

//Function for handling message view
//@param result the JSON response returned from API routes
function create_message(result){
  //Clear all the message in message view
  document.querySelector('#message-view').innerHTML = '';

  //Create and style message item
  const message = document.createElement('p');
  message.style.padding = '10px';
  message.style.paddingLeft = '20px';
  message.style.borderRadius = '10px';

  //If successful
  if (result['message']) {
    //Add returned message to message item
    message.innerHTML = result['message'];
    message.style.backgroundColor = 'rgb(176, 225, 255)';
    //Manual redirect so the address wouldn't have csrf token
    window.location.href = '';


  }
  //If error
  else {
    //Add returned error to message item
    message.innerHTML = result['error'];
    message.style.backgroundColor = 'rgb(255, 188, 176)';

  }

  //Add message item to message view
  document.querySelector('#message-view').append(message);
  document.querySelector('#message-view').style.display = 'block';
}

//Changing heart shape opacity for like function
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

