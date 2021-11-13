// TO DO:  Citation comments, etc.

// Initial page load
document.addEventListener('DOMContentLoaded', function () {
  // alert('DOMContentLoaded');

  // Add listeners to the Like/Unlike buttons
  document.querySelectorAll('.like-button').forEach(button => {
    button.addEventListener('click', () => toggleLike(button.dataset.post));
  });

  // Add listeners to the Edit buttons
  document.querySelectorAll('.edit-button').forEach(button => {
    button.addEventListener('click', () => editPost(button.dataset.post));
  });

  // Add a listener to the Follow/Unfollow button,
  const followButton = document.querySelector('#follow-button');
  followButton.addEventListener('click', () => toggleFollow(followButton.dataset.user));

});


/**
 * Like or unlike a post
 * @param {number} id - The ID of the post to be retrieved
 */

// TO DO:  Add comments about toggle vs. passing the action

   function toggleLike(id) {

    // Disable the button the user just clicked on, so they can't click repeatedly while waiting
    const likeButton = document.querySelector(`.post-row[data-post="${id}"] .like-button`);
    likeButton.disabled = true;

    // Toggle the post's like status via the API
    fetch(`/likes/${id}`)
      .then(response => response.json())
      .then(post => {


        // If successful, receive the new post stats and update what the user sees
        // TO DO:  see if we can get the exact error code instead of checking for whether the error exists
        if (post.error == undefined){
          // Style the Like Button to reflect the new like status
          // TO DO:  Replace button text with icons?
          const user_id = JSON.parse(document.getElementById('user_id').textContent);
          if (user_id in post.likers) {
            // Style the button for UNLIKE
            likeButton.innerHTML = 'Unlike';
          } else {
            // Style the button for LIKE
            likeButton.innerHTML = 'Like';
          }
          // Update the likes count
          document.querySelector(`.post-row[data-post="${id}"] .likes-count`).innerHTML = post.likes_count
        } else {
          alert(post.error);
          // TO DO:  Show an on-screen 'please try again' message
        }

        // Reenable the like/dislike button
        likeButton.disabled = false;
      });

   }



/**
 * Follow or unfollow a user
 * @param {number} id - The ID of the user to be followed
 */

// TO DO:  Make sure that we disable & reenable buttons as needed

 function toggleFollow(id) {

    // Disable the button the user just clicked on, so they can't click repeatedly while waiting
    const followButton = document.querySelector('#follow-button');
    followButton.disabled = true;

    // Toggle the profile's followed status via the API
    fetch(`/follows/${id}`)
      .then(response => response.json())
      .then(profile => {


        // If successful, receive the new following stats and update what the user sees
        // TO DO:  see if we can get the exact error code instead of checking for whether the error exists
        if (profile.error == undefined){

          // Style the Follow/Unfollow button to reflect the new following status
          // TO DO:  Replace button text with icons?
          const user_id = JSON.parse(document.getElementById('user_id').textContent);
          if (user_id in profile.followers) {
            // Style the button for UNFOLLOW
            followButton.innerHTML = 'Unfollow';
          } else {
            // Style the button for FOLLOW
            followButton.innerHTML = 'Follow';
          }
          // Update the follow counts
          document.querySelector('#followers-count').innerHTML = profile.followers_count
          document.querySelector('#following-count').innerHTML = profile.following_count

        } else {
          alert(profile.error);
          // TO DO:  Show an on-screen 'please try again' message
        }

        // Reenable the like/dislike button
        followButton.disabled = false;
      });
}


/**
 * Provide the user with a JS "form" to edit a post
 * @param {number} id - The ID of the post to be edited
 */

 function editPost(id) {

  // Disable the button the user just clicked on, so they can't click repeatedly while waiting
  const editButton = document.querySelector(`.post-row[data-post="${id}"] .edit-button`);
  editButton.disabled = true;

  // Replace the content with an edit box, populated with the post contents
  const contents = document.querySelector(`.post-row[data-post="${id}"] .post-content`);
  const contentsValue = contents.innerHTML;
  // TO DO:  Do we still need edit-content class?
  // contents.classList.add('edit-content');
  contents.innerHTML = '';
  const child = document.createElement('textarea');
  child.value = contentsValue;
  contents.appendChild(child);


  // Add a save button
  const saveButton = document.createElement('button');
  saveButton.id = 'save-button';
  saveButton.innerHTML = 'Save';
  saveButton.addEventListener('click', () => updatePost(id));
  contents.appendChild(saveButton);

}


/**
 * Update an edited post
 * @param {number} id - The ID of the post to be updated
 */

// CITATION:  based on markRead from provided inbox.js in Project 3

// TO DO:  Make sure that we disable & reenable buttons as needed

function updatePost(id) {

  // Disable the save button
  const saveButton = document.querySelector('#save-button');
  saveButton.disabled = true;

  // Update the post's contents via the API

  fetch(`/posts/${id}`, {
    method: 'PUT',
    body: JSON.stringify({
      content: document.querySelector(`.post-row[data-post="${id}"] textarea`).value
    })
  })
  .then(response => response.json())
  .then(post => {


    // If successful, update the page
    // TO DO:  see if we can get the exact error code instead of checking for whether the error exists
    if (post.error == undefined){
      // alert('success!');

      // Replace the "form" with the updated post contents
      const contents = document.querySelector(`.post-row[data-post="${id}"] .post-content`);
      contents.innerHTML = post.content

      // Reenable the edit button
      const editButton = document.querySelector(`.post-row[data-post="${id}"] .edit-button`);
      editButton.disabled = false;

    } else {
      alert(post.error);
      // TO DO:  Show an on-screen 'please try again' message
    }

    // Reenable the like/dislike button to try again
    saveButton.disabled = false;

      
  });

}
