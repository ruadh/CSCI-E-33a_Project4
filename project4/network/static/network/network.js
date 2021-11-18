// Initial page load
document.addEventListener('DOMContentLoaded', function () {

  // Add listeners to the Like/Unlike buttons
  document.querySelectorAll('.like-button').forEach(button => {
    button.addEventListener('click', () => toggleLike(button.dataset.post));
  });

  // Add listeners to the Edit buttons
  document.querySelectorAll('.edit-button').forEach(button => {
    button.addEventListener('click', () => loadPost(button.dataset.post));
  });

  // NOTE: IDs should be unique on the page, but I'm using querySelectorAll for the follow & submit buttons anyway. 
  //       If we just used querySelector, we'd get JS errors when the element is not present on the page.  
  //       querySelectorAll().forEach handles that seamlessly.  The consistency also improves readability.

  // Add a listener to the profile Follow/Unfollow button
  document.querySelectorAll('#follow-button').forEach(button => {
    button.addEventListener('click', () => toggleFollow(button.dataset.user));
  });

  // Add a listener to the new post Submit button 
  document.querySelectorAll('#submit-post').forEach(button => {
    button.addEventListener('click', () => newPost());
  });

});


/**
 * Create a new post
 */

// CITATION:  adapted from markRead from inbox.js provided in Project 3

function newPost() {

  // Prevent normal form submission, which would refresh the page
  event.preventDefault();

  // Gather and validate the content
  const content = document.querySelector('#new-post textarea').value.trim();
  const valid = validate(content, document.querySelector('#main-alert-fading'));

  if (valid == true) {
    // Disable the submit button
    const saveButton = document.querySelector('#submit-post');
    saveButton.disabled = true;

    // Gather the CSRF token from the Django template
    // CITATION:  Copied directly from Vlad's section slides
    const token = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    // Update the post's contents via the API
    fetch(`/posts`, {
        method: 'POST',
        body: JSON.stringify({
          content: content
        }),
        headers: {
          'X-CSRFToken': token
        }
      })
      .then(response => response.json())
      .then(post => {

        // If successful, reload the page to get 1st page of the latest posts
        if (post.error == undefined) {
          location.reload();

        } else {
          // Show a message in the main alert area
          // DESIGN NOTE:  I'm repeating a queryselector, but I think that's better than storing the object,
          //                since this block will not usually be executed - only if there's an error.
          displayAlert(document.querySelector('#main-alert-fading'), post.error, 'danger');

        }

        // Reenable the like/dislike button to try again
        saveButton.disabled = false;

      });
  }

}


/**
 * Provide the user with a JS pseudo-form to edit a post
 * @param {number} id - The ID of the post to be edited
 */

function loadPost(id) {

  // Disable the button the user just clicked on, so they can't click repeatedly while waiting
  const editButton = document.querySelector(`.post-row[data-post="${id}"] .edit-button`);
  editButton.disabled = true;

  // Replace the content with an edit box, populated with the post contents
  const contents = document.querySelector(`.post-row[data-post="${id}"] .post-content`);
  const contentsValue = contents.innerHTML;
  contents.innerHTML = '';
  const child = document.createElement('textarea');
  child.value = contentsValue;
  contents.appendChild(child);


  // Add a save button
  const saveButton = document.createElement('button');
  saveButton.classList.add('btn', 'btn-primary');
  saveButton.id = 'save-button';
  saveButton.innerHTML = 'Save';
  saveButton.addEventListener('click', () => updatePost(id));
  contents.appendChild(saveButton);

}


/**
 * Update an edited post
 * @param {number} id - The ID of the post to be updated
 */

// CITATION:      Based on markRead inbox.js provided in Project 3
// DESIGN NOTE:   I decided not to merge newPost and updatePost into a single function.
//                While the fetch is pretty similar, how the function updates the
//                DOM afterward is pretty different for the top-of-page and in-row "forms".

function updatePost(id) {

  // Gather and validate the content
  const content = document.querySelector(`.post-row[data-post="${id}"] textarea`).value.trim();
  const valid = validate(content, document.querySelector(`.post-row[data-post="${id}"] .alert`));

  if (valid == true) {
    // Disable the save button
    const saveButton = document.querySelector('#save-button');
    saveButton.disabled = true;

    // Gather the CSRF token from the Django template
    // CITATION:  Copied directly from Vlad's section slides
    const token = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    // Update the post's contents via the API
    fetch(`/posts/${id}`, {
        method: 'PUT',
        body: JSON.stringify({
          content: content
        }),
        headers: {
          'X-CSRFToken': token
        }
      })
      .then(response => response.json())
      .then(post => {


        // If successful, update the page
        if (post.error == undefined) {

          // Replace the pseudo-form with the updated post contents
          const contents = document.querySelector(`.post-row[data-post="${id}"] .post-content`);
          contents.innerHTML = post.content;

          // Reenable the edit button
          const editButton = document.querySelector(`.post-row[data-post="${id}"] .edit-button`);
          editButton.disabled = false;

        } else {
          // Display an alert above the post
          // DESIGN NOTE:  I'm repeating a queryselector, but I think that's better than storing the object,
          //               since this block will not usually be executed - only if there's an error.
          displayAlert(document.querySelector(`.post-row[data-post="${id}"] .alert`), post.error, 'danger');

        }

        // Reenable the like/dislike button to try again
        saveButton.disabled = false;

      });
  }

}


/**
 * Like or unlike a post
 * @param {number} id - The ID of the post
 */

// DESIGN NOTES: Toggling the existing value means that we might misinterpret the user's intention in some cases. 
//               Ex: if the user has our app open two browser windows, a like made in one window would still seem
//               not liked in the other window until refreshed/updated.  So the user might try to like it a second
//               time, and end up undoing their first like.  Another way to handle that would be to pass the user's 
//               intended action (like/unlike) to the API, but since Vlad suggested the toggle method in section,
//               I assume it's acceptable, and am not prioritizing covering that scenario.

function toggleLike(id) {

  // Disable the button the user just clicked on, so they can't click repeatedly while waiting
  const likeButton = document.querySelector(`.post-row[data-post="${id}"] .like-button`);
  likeButton.disabled = true;

  // Toggle the post's like status via the API
  fetch(`/likes/${id}`)
    .then(response => response.json())
    .then(post => {

      // If successful, receive the new post stats and update what the user sees
      if (post.error == undefined) {
        // Style the Like Button to reflect the new like status
        const userId = JSON.parse(document.getElementById('user_id').textContent);
        if (post.likers.includes(userId)) {
          // Style the button for UNLIKE
          likeButton.innerHTML = '&#10084;&#65039; <span class="sr-only">Unlike this post</span>';
        } else {
          // Style the button for LIKE
          likeButton.innerHTML = '&#129293; <span class="sr-only">Like this post</span>';
        }
        // Update the likes count
        document.querySelector(`.post-row[data-post="${id}"] .likes-count`).innerHTML = `${post.likers.length} ${post.likers.length !== 1 ? 'Likes' : 'Like'}`;
      } else {
        // Display an alert above the post
        displayAlert(document.querySelector(`.post-row[data-post="${id}"] .alert`), post.error, 'danger');
      }

      // Reenable the like/dislike button
      likeButton.disabled = false;
    });

}


/**
 * Follow or unfollow a user
 * @param {number} id - The ID of the user to be followed
 */

// DESIGN NOTE:   This is very similar to toggleLike, so I tried merging them, but decided to keep them separate.
//                The fetch is similar, but they interact with the DOM differently, and the merged version's
//                branching logic was harder to read, which is bad for maintainability.

function toggleFollow(id) {

  // Disable the button the user just clicked on, so they can't click repeatedly while waiting
  const followButton = document.querySelector('#follow-button');
  followButton.disabled = true;

  // Toggle the profile's followed status via the API
  fetch(`/follows/${id}`)
    .then(response => response.json())
    .then(profile => {


      // If successful, receive the new following stats and update what the user sees
      if (profile.error == undefined) {

        // Style the Follow/Unfollow button to reflect the new following status
        const userId = JSON.parse(document.getElementById('user_id').textContent);
        if (profile.followers.includes(userId)) {
          followButton.innerHTML = 'Unfollow';
        } else {
          followButton.innerHTML = 'Follow';
        }
        // Update the follow counts
        document.querySelector('#followers-count').innerHTML = profile.followers.length;
        document.querySelector('#following-count').innerHTML = profile.following_count;

      } else {
        // Show a message in the main alert area
        displayAlert(document.querySelector('#main-alert-fading'), profile.error, 'danger');
      }

      // Reenable the follow/unfollow button
      followButton.disabled = false;
    });
}


// HELPER FUNCTIONS


/** Display an alert message in the specified element with the specified content and Bootstrap style
 * 
 * @param {object} element - the HTML element object to contain the message
 * @param {string} message - the message to be displayed 
 * @param {string} style - the Bootstrap alert style, ex 'danger' for style 'alert-danger'
 * 
 * For style options see:  https://getbootstrap.com/docs/4.0/components/alerts/
 */

// DESIGN NOTE:   I'm using display styling and CSS animations to dismiss the alert.  
//                It would be cool to use Boostrap's JQuery, but since this isn't in the spec, it wasn't a priority

function displayAlert(element, message, style) {
  element.innerHTML = message;
  element.style.display = 'block';
  element.classList.add('alert', `alert-${style}`);

  // Pause for the fade out animation, then clear the contents and remove the element
  setTimeout(() => {
      element.innerHTML = null;
      element.style.display = 'none';
    },
    // DEPENDENCY:  This must be updated if the animation timing or duration for .alert in styles.css are modified
    7000
  );

}

/** Check the contents of a post to be created or edited and show an error
 * 
 * @param {string} content - the post content to be validated 
 * @param {object} element - the HTML element object to contain the any error messages
 * 
 * Returns True if validation passes, or False if validation fails
 * 
 */

// DESIGN NOTE:   I'm using this instead of Django's form validation to avoid page refreshes,
//                and to keep the error handling consistent across posts, likes, and follows.

function validate(content, element) {
  const CHARACTER_LIMIT = JSON.parse(document.getElementById('CHARACTER_LIMIT').textContent);
  if (content.length == 0) {
    // Show a message in the main alert area
    displayAlert(element, 'Empty posts are not allowed', 'danger');
    return false;

  } else if (content.length > CHARACTER_LIMIT) {
    // Show a message in the main alert area
    displayAlert(element, `Posts may not exceed ${CHARACTER_LIMIT} characters.`, 'danger');
    return false;

  } else {
    return true;
  }

}
