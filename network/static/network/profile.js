document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('input[type=button]') != null) {
        document.querySelector('input[type=button]').addEventListener('click', event => {
            event.preventDefault();
            follow();
        });
}
});


function follow(){
    
    const profile_name = document.querySelector('#name').innerHTML;

    const count = parseInt(document.querySelector('#fo').innerHTML.split(':')[1]);

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

            document.querySelector('input[type=button]').value = "Follow";
            document.querySelector('#fo').innerHTML=`Follower: ${count_follower(false, count)}`
        }
        else if (parsed.message === "Followed."){

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

