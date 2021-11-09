// Initial page load
document.addEventListener('DOMContentLoaded', function () {

    // Show the new post form only if the user is logged in
    // CITATION:  Learned about json_script from: https://stackoverflow.com/a/62592463
    const authenticated = JSON.parse(document.getElementById('authenticated'));
    if (authenticated == true) {
      // Show the new post form
      document.querySelector('#new-post').style.display = 'block';
      // Have JS handle the submit button action instead of submitting the page
      document.querySelector('#post-form').addEventListener('submit', submitPost);
      // Disable the Submit button until content is entered
      document.querySelector('#submit-post').disabled = true;
      document.querySelector('#compose-post').addEventListener('keyup', enableSubmit);
    } else {
      document.querySelector('#new-post').style.display = 'none';
    }


  
    // TO DO:  Load the posts list
  });


/**
 * Disable the submit button when the content field is empty
 */

 function enableSubmit() {

  const recipients = document.querySelector('#compose-post');
  if (recipients.value.length > 0) {
    document.querySelector('#submit-post').disabled = false;
  } else {
    document.querySelector('#submit-post').disabled = true;
  }

}

/**
 * Load one page of posts
 */

 function listPosts() {

  // TO DO

}


  /**
 * Submit the post form
 */

function submitPost() {

    // Prevent the user from repeatedly pressing the Submit button if there is a delay
    document.querySelector('#submit-post').disabled = true;

    // Prevent normal form submission, which would refresh the page
    event.preventDefault();

    // Gather the form value
    const form = document.querySelector('#post-form');
    const content = form.querySelector('#compose-post').value;

    // Save the post via the API
    fetch('/posts', {
      method: 'POST',
      body: JSON.stringify({
        content: content
      })
    })
    .then(response => response.json())
    .then(result => {
      // Load the latest posts list or show an error
      const error = result.error;
      if (error !== undefined) {
        alert(error);
        // Reenable the Submit button so the user can try again
        document.querySelector('#submit-post').disabled = false;
      } else {
        listPosts();
        // TO DO:  Display message
        const message = result.message;
        // TEMP FOR TESTING
        alert(message);
      }
    });
  
  }
