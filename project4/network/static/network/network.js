/** 
 * Unlike my previous assignments, I did not submit Project 4 before dropping the Fall 2021 offering,
 * so I have not received grading feedback on any of this work.
 * 
 * Much of this code is recycled from my work on earlier projects (some of which benefitted from grading feedback),
 * but since I cited that feedback in the earier projects, I didn't call it out a second time here.
 * 
 * Some of my code is adapted from the starter files in earlier projects or was helped by content I found on the internet.
 * Those are called out with 'CITATION' in the comments.
*/

// Initial page load
document.addEventListener('DOMContentLoaded', function () {

    // Load the first page of posts
    loadPosts();

    // Add new post form: limited to authenticated users, handled by JS, disabled until content is entered
    // CITATION:  Learned about json_script from: https://stackoverflow.com/a/62592463
    const authenticated = JSON.parse(document.getElementById('authenticated').textContent);    
    if (authenticated == true) {
      document.querySelector('#new-post').style.display = 'block';
      document.querySelector('#post-form').addEventListener('submit', submitPost);
      document.querySelector('#submit-post').disabled = true;
      document.querySelector('#compose-post').addEventListener('keyup', enableSubmit);
    } else {
      document.querySelector('#new-post').style.display = 'none';
    }

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
 * Create a new HTML element with the specified innerHTML and optional classes
 * @param {string} element - The type of HTML element to be created
 * @param {string} innerHTML - The inner HTML to be added to the new element
 * @param {string} [cssClass] - A space-delimited list of classes to be added to the new element
 * 
 * NOTE: It would also be useful to support adding the event listeners here,
 * but passing a function with an unknown number of parameters is beyond my skills right now.
 */

 function newElement(element, innerHTML, cssClass = null) {
  const child = document.createElement(element);
  child.innerHTML = innerHTML;
  if (cssClass !== null) {
    cssClass.split(' ').forEach(cssClass => {
      child.classList.add(cssClass);
    });
  }
  return child;
}


/**
 * Load the specified page of posts
 * @param {string} page - The number of the page to be loaded 
 */

 function loadPosts(page=1) { 
  
  // TO DO:  PAGINATION  (or is it in JS?)

  // If the list is already present, clear it
  document.querySelector('#posts-view').innerHTML = 'Loading Posts...';

  // Create a container element for the post lines
  const postList = newElement('div', 'Loading Posts...');
  postList.id = 'posts-view';


  // TO DO:  Decide if we need to disable any buttons during the fetch
  // document.querySelectorAll('.loading-disable').forEach(button => {
  //   button.disabled = true;
  // });

  // Get the posts via the API
  fetch(`/posts/${page}`)
    .then(response => response.json())
    .then(posts => {

      // Clear the loading message and show the post count instead
      postList.innerHTML = '';
      const count = posts.length;

      // Create a summary line for each post
      if (count > 0) {
        posts.forEach(post => {

          // Create and populate the post row
          const summary = newElement('div', null, 'post-row');
          summary.appendChild(newElement('div', `${post.content}`));
          summary.appendChild(newElement('span', `By:  ${post.author}`, 'post-author'));
          summary.appendChild(newElement('span', `&emsp;${post.timestamp}`, 'post-timestamp'));
          summary.appendChild(newElement('span', `&emsp;${post.likes_count} Like${(post.likes_count === 1 ? '' : 's')}`));

          // TO DO:  Add a like button

          // Add the full post row to the div 
          postList.appendChild(summary);

        });
      }

      // TO DO:  Reenable any disabled buttons
      // document.querySelectorAll('.loading-disable').forEach(button => {
      //   button.disabled = false;
      // });

    

    });

  // Replace the loading message with the new list of posts
  // CITATION:  https://www.javascripttutorial.net/dom/manipulating/replace-a-dom-element/
  document.querySelector('#posts-view').parentNode.replaceChild(postList, document.querySelector('#posts-view'))

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

        // Clear the post form
        document.querySelector('#compose-post').value = null;

        // Refresh the list of posts
        loadPosts();

        // TO DO:  Display message on screen
        const message = result.message;
        // alert(message);

        // TEMP FOR TESTING
        
      }
    });
  
  }


