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

   function toggleLike(id) {
     alert(id);
   }

/**
 * Follow or unfollow a user
 * @param {number} id - The ID of the user to be followed
 */

 function toggleFollow(id) {
  alert(id);
}

/**
 * Edit a post
 * @param {number} id - The ID of the post to be edited
 */

 function editPost(id) {
  alert(id);
}
