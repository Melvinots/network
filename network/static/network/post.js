
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}

const csrfToken = getCookie('csrftoken');


document.addEventListener('DOMContentLoaded', () => {
  const profile = document.querySelector('#profile');
  const postView = document.querySelector('#post-view');
  const form = document.querySelector('.container');

  if (form) {
    const myButton = document.querySelector('.post-button');
    const myContent = document.querySelector('#content');

    myButton.disabled = true;
    myButton.style.opacity = '50%';

    myContent.onkeyup = () => {
      if (myContent.value.length > 0) {
          myButton.disabled = false;
          myButton.style.opacity = '100%';
      } else {
          myButton.disabled = true;
          myButton.style.opacity = '50%';
      }
    }
  }

  if (postView) {
    postView.addEventListener('click', (event) => {
      if (event.target.classList.contains('post-edit')) {

        // For editing the post
        const postContent = event.target.parentElement.nextElementSibling;
  
        const postText = postContent.querySelector('.post-text');
        const editTextarea = postContent.querySelector('.edit-textarea');
        const saveButton = postContent.querySelector('.save-button');
        
        postText.style.display = 'none';
        editTextarea.style.display = 'block';
        saveButton.style.display = 'block';
  
        editTextarea.focus();
        const post_id = editTextarea.dataset.text;
  
        saveButton.addEventListener('click', () => {
          fetch(`/posts/${post_id}`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
              content: editTextarea.value
            })
          })
  
          postText.innerHTML = editTextarea.value;
          postText.style.display = 'block';
          editTextarea.style.display = 'none';
          saveButton.style.display = 'none';
  
        })
      } else if (event.target.classList.contains('bi')) {

          // For liking the post
          event.target.classList.toggle('bi-heart');
          event.target.classList.toggle('bi-heart-fill')
          const numLikes = event.target.parentElement.nextElementSibling;
  
          const post_id = event.target.dataset.like;
          fetch(`/posts/${post_id}`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({})
          })
          .then(response => response.json())
          .then(data => {
            numLikes.innerHTML = `${data.likes} Likes`;
          })
        }
    })
  } 

  if (profile) {
      profile.addEventListener('click', (event) => {

        // For updating followers/followings
        if (event.target.classList.contains('follow-button')) {
          const numFollowers = event.target.previousElementSibling.firstElementChild;

          const username = event.target.dataset.profilename;
          fetch(`/profile/${username}/1`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrfToken
            }
          })
          .then(response => response.json())
          .then(data => {
            numFollowers.innerHTML = `${data.followers} followers`;
            event.target.innerHTML = data.text;
          })
        }
      })
  }
})
