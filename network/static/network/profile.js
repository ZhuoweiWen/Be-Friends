// Script for handling profile page user interface

document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('input[type=button]') != null) {
        document.querySelector('input[type=button]').addEventListener('click', event => {
            event.preventDefault();
            follow();
        });
}
});


function follow(){
    //Get profile owner name
    const profile_name = document.querySelector('#name').innerHTML;

    //Get follower count
    const count = parseInt(document.querySelector('#fo').innerHTML.split(':')[1]);

    //Handlee csrf token and request
    const csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value
    const request = new Request(
        '/follow',
        {headers: {'X-CSRFToken': csrftoken}}
      );

    fetch(request,{
        method: 'POST',
        body: JSON.stringify({
            profile_name: profile_name,
        })
    })
    .then(response => response.text())
    .then(result => {
        //Change button value when followed and unfollowed"
        console.log(result);
        //parse returned result
        const parsed = JSON.parse(result)
        if (parsed.message === "Unfollowed."){
            //Change button text and update count
            document.querySelector('input[type=button]').value = "Follow";
            document.querySelector('#fo').innerHTML=`Follower: ${count_follower(false, count)}`
        }
        else if (parsed.message === "Followed."){
            //Change button text and update count
            document.querySelector('input[type=button]').value = "Unfollow";
            document.querySelector('#fo').innerHTML=`Follower: ${count_follower(true, count)}`
        }
    })
}

//Helper function for counting follower when user is following
//the profile owner
//@param fo the boolean whether user is following or unfollowing
//@param count the current follower number
function count_follower(fo, count){
    
    if (fo === true){
        count++;
        return count;
    }
    else {
        count--;
        return count;
    }
}

