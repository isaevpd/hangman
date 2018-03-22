
const form = document.querySelector('form');
const letterInput = document.querySelector('input');
const wordElem = document.querySelector('div#word-elem');
const attemptsElem = document.querySelector('div#attempts-left');
const info = document.querySelector('div#info');
const lettersUsedEl = document.querySelector("div#letters-used");
const availableLetters = document.querySelector(
  "div#available-letters"
)
const status = document.querySelector("h3#status");
const originalWordEl = document.querySelector("h2#original-word");
const tryAgain = document.querySelector("h3#try-again");
const msg = {
  won: "You won!",
  lost: "You lost!"
}

let showMessageTimer;

function hide(...elems) {
  elems.forEach(el => el.style.display = "none");
}

function getLettersUsed(availableLetters) {
  const alphabet = "abcdefghijklmnopqrstuvwxyz";
  return alphabet.split("").filter(
    letter => !(availableLetters.indexOf(letter) !== -1)
  ).join(" ").toUpperCase();
}

function toHumanReadable(s) {
  s = s.replace("_", " ");
  return s.charAt(0).toUpperCase() + s.slice(1);
}

function setMessageStyle(elem) {
  elem.style.visibility = "visible";
  options = { 
    "Correct guess": "green",
    "Already guessed": "blue",
    "Incorrect guess": "red"
  }
  elem.style.color = options[elem.textContent]
}

function render(data) {
  letterInput.focus();
  clearTimeout(showMessageTimer);

  wordElem.textContent = data.representation.split("").join(" ");

  attemptsElem.textContent = "Attempts left: " + data.attempts_left;

  const lettersUsed = getLettersUsed(data.available_letters);
  if (lettersUsed !== "") {
    lettersUsedEl.textContent = lettersUsed;
  }

  const lettersLeft = data.available_letters.toUpperCase().split("").join(" ");
  availableLetters.textContent = lettersLeft;

  if (data.message) {
    info.textContent = toHumanReadable(data.message);
    setMessageStyle(info)
    showMessageTimer = setTimeout(() => { info.style.visibility = "hidden"; }, 3000);
  }
  if (data.status == "won" || data.status == "lost") {
    hide(document.querySelector("div#main"))
    document.cookie = "hangman_game_id" + '=;expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    status.textContent = msg[data.status] + status.textContent;
    status.style.display = "";
    originalWordEl.textContent = data.original_word;
    tryAgain.style.display = "";

  }
}

if (document.cookie.indexOf("hangman_game_id") === -1) {
  fetch(
    '/api/v1/word', { method: 'POST', credentials: 'same-origin' }
  ).then(
    res => res.json()
  ).then(
    json => render(json)
  );
}
else {
  fetch(
    '/api/v1/letter',
    { method: 'GET', credentials: 'same-origin' }
  ).then(
    res => res.json()
  ).then(
    json => render(json)
  )
}

form.addEventListener('submit', event => {
  event.preventDefault()
  const letter = letterInput.value;
  if (letter === '') {
    return
  }
  letterInput.value = '';
  fetch(
    '/api/v1/letter', {
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      credentials: 'same-origin',
      method: 'POST',
      body: JSON.stringify({ letter }),
    }
  ).then(
    res => {
      if (res.redirected) {
        window.location.replace(res.url);
      }
      else if (res.ok) return res.json()
      else return Promise.reject(res.json())
    }
    ).then(
      json => {
        return render(json)
    }
    ).catch(
      error => {
       return Promise.resolve(); 
      }
    )
});
