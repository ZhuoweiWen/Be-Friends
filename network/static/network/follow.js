document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('input[type=button]').forEach
    (element => element.addEventListener('click', event => {
      event.preventDefault();
      follow(event);
    }));
});



function follow(event){

    const profile_name = event.target.parentElement.children[0].innerHTML;
    const count = document.querySelector('#fo').innerHTML;
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
        //To do" Change button text when followed and unfollowed"
        console.log(result);
        const parsed = JSON.parse(result)
        if (parsed.message === "Unfollowed."){

            event.target.value = "Follow";
            document.querySelector('#fo').innerHTML=`${count_follower(false, count)}`
        }
        else if (parsed.message === "Followed."){

           event.target.value = "Unfollow";
            document.querySelector('#fo').innerHTML=`${count_follower(true, count)}`
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