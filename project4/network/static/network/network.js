// TO DO:  Citation comments, etc.

// Initial page load
document.addEventListener('DOMContentLoaded', function () {

    // Add functionality that is limited to logged-in users:
    // CITATION:  Learned how to get auth status from: https://stackoverflow.com/a/62592463
    const authenticated = JSON.parse(document.getElementById('authenticated').textContent);    
    if (authenticated == true) {

      // Add listeners to the Like/Unlike buttons
      document.querySelectorAll('.like-button').forEach(button => {
        button.addEventListener('click', () => submitLike(button.dataset.post));
      });

    } else {
      document.querySelector('#new-post').style.display = 'none';
    }

  });

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
 * Like or unlike a post
 * @param {number} id - The ID of the post to be retrieved
 * @param {string} action - The 
 */

   function submitLike(id, action) {
     alert(id);
   }

