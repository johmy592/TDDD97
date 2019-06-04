var webSocket;

connectWebsocket = function (email) {
    webSocket = new WebSocket('ws://'+ document.domain + ':5000/api');

    webSocket.onopen = function () {
        webSocket.send(email);
    };
    webSocket.onmessage = function (ev) {
        console.log(ev.data.toString());
        if (ev.data === 'Force log out.') {
            if (localStorage.getItem('token') !== null) {
                sign_out(ev);
                webSocket.close(1, "Signed out.")
            }
        }
    };
};

displayView = function () {
    if (localStorage.getItem("token") === null) {
        document.getElementById("display_view").innerHTML = document.getElementById("welcomeview").innerHTML;

        document.getElementById('login_form').addEventListener('submit', logIn);
        document.getElementById('signup_form').addEventListener('submit', registerUser);
        document.getElementById('signup_email').addEventListener('input', resetValidation);

        document.getElementById('signup_password').addEventListener('input',
            function () {
                passwordLength('signup_password')
            });
        document.getElementById('repeat_password').addEventListener('input',
            function () {
                passwordMatch('signup_password', 'repeat_password')
            });
    } else {

        document.getElementById("display_view").innerHTML = document.getElementById("profileview").innerHTML;
        getUserData();
        updateWall('message_wall');


        document.getElementById('home_tab_btn').addEventListener('click', function(ev){showTab(ev, 'home_tab')});
        document.getElementById('browse_tab_btn').addEventListener('click', function(ev){showTab(ev, 'browse_tab')});
        document.getElementById('account_tab_btn').addEventListener('click', function(ev){showTab(ev, 'account_tab')});

        document.getElementById('message_button').addEventListener('click',
            function () {
                sendMessage('message_box', 'email_info', 'message_wall')
            });
        document.getElementById("browse_user").addEventListener('submit', browseUser);
        document.getElementById('send_browse_msg').addEventListener('click',
            function () {
                sendMessage('browse_message_box', 'user_email', 'browse_message_wall')
            });
        document.getElementById('reload_browse_wall_btn').addEventListener('click',
            function () {
                updateWall('browse_message_wall')
            });
        document.getElementById('reload_wall_button').addEventListener('click',
            function () {
                updateWall('message_wall')
            });
        document.getElementById('password_change').addEventListener('submit', changePassword);


        document.getElementById('new_password').addEventListener('input',
            function () {
                passwordLength('new_password')
            });
        document.getElementById('confirm_new_pw').addEventListener('input',
            function () {
                passwordMatch('new_password', 'confirm_new_pw')
            });
        document.getElementById('sign_out').addEventListener('submit', logOut);

        //Explicitly call click() to show the home page
        document.getElementById("home_tab_btn").click();
    }

};

window.onload = function () {
    displayView();
    // Validator and login/register functionality.

    //code that is executed as the page is loaded.
    //You shall put your own custom code here.
    //window.alert() is not allowed to be used in your implementation.
};

/* Switching tabs */
showTab = function (evt, tab) {
    var i, content, tab_buttons;
    //Make all tabs hidden
    content = document.getElementsByClassName('tab_content');
    for (i = 0; i < content.length; i++) {
        content[i].style.display = "none";
    }

    //Make all tabs inactive
    tab_buttons = document.getElementsByClassName('tab_button');
    for (i = 0; i < tab_buttons.length; i++) {
        tab_buttons[i].className = tab_buttons[i].className.replace(" active", "");
    }
    // Show the specified tab
    document.getElementById(tab).style.display = "block";
    evt.currentTarget.className += " active";
};


/* Retrieves information about user for home page */
getUserData = function () {
    var token = localStorage.getItem('token');
    var serverResponse = serverstub.getUserDataByToken(token).data;
    var email = serverResponse.email;
    var name = serverResponse.firstname;
    var family_name = serverResponse.familyname;
    var gender = serverResponse.gender;
    var city = serverResponse.city;
    var country = serverResponse.country;

    document.getElementById('email_info').innerText = email;
    document.getElementById('name_info').innerText = name + " " + family_name;
    document.getElementById('gender_info').innerText = gender;
    document.getElementById('city_info').innerText = city;
    document.getElementById('country_info').innerText = country;

};


sendMessage = function (message_input, receiver_email, msg_wall) {
    var token = localStorage.getItem('token');
    var message = document.getElementById(message_input).value;
    var email = document.getElementById(receiver_email).innerText;
    serverstub.postMessage(token, message, email);
    updateWall(msg_wall);
};

updateWall = function (msg_wall) {
    var token = localStorage.getItem('token');
    var messages;

    if (msg_wall === 'message_wall'){
      // Posting to your own wall
      messages = serverstub.getUserMessagesByToken(token).data;
    }else {
        // Posting to someone elses wall
        var email = document.getElementById('user_email').innerText;
        messages = serverstub.getUserMessagesByEmail(token, email).data;
    }

    document.getElementById(msg_wall).innerHTML = "";
    var i;
    for (i = 0; i < messages.length; i++) {
        var content = messages[i].content;
        var writer = messages[i].writer;

        document.getElementById(msg_wall).innerHTML += "<textarea readonly class='posted_message'>" + writer +
            ": " + content + "</textarea>";
    }
};


browseUser = function (event) {
    event.preventDefault();
    // Reset error message if any exists
    document.getElementById('user_not_found').innerText = "";

    var token = localStorage.getItem('token');
    var browse_email = document.getElementById('search_email').value;
    var serverResponse = serverstub.getUserDataByEmail(token, browse_email);

    if (serverResponse.success) {
        var name = serverResponse.data.firstname;
        var family_name = serverResponse.data.familyname;
        var email = serverResponse.data.email;
        var gender = serverResponse.data.gender;
        var city = serverResponse.data.city;
        var country = serverResponse.data.country;
        document.getElementById('user_name').innerText = name + " " + family_name;
        document.getElementById('user_email').innerText = email;
        document.getElementById('user_gender').innerText = gender;
        document.getElementById('user_city').innerText = city;
        document.getElementById('user_country').innerText = country;

        // Update message wall, then display the correct user profile
        updateWall('browse_message_wall');
        document.getElementById('user_profile').style.display = "block";
    } else {
        document.getElementById('user_profile').style.display = "none";
        document.getElementById('user_not_found').innerText = serverResponse.message;
    }
};


logOut = function (event) {
    event.preventDefault();
    serverstub.signOut(localStorage.getItem("token"));
    localStorage.removeItem("token");
    displayView();
};


changePassword = function (event) {
    event.preventDefault();
    var old_password = document.getElementById("old_password").value;
    var new_password = document.getElementById("new_password").value;
    var serverResponse = serverstub.changePassword(localStorage.getItem("token"), old_password, new_password);
    document.getElementById("new_pwd_feedback").innerHTML = serverResponse.message;
    if (serverResponse.success) {
        document.getElementById('old_password').value = '';
        document.getElementById('new_password').value = '';
        document.getElementById('confirm_new_pw').value = '';
    }
};


logIn = function (event) {
    event.preventDefault();
    var login_email = document.getElementById('login_email');
    var login_password = document.getElementById('login_password');
    var serverResponse = serverstub.signIn(login_email.value, login_password.value);
    if (!serverResponse.success) {
        document.getElementById("login_error").innerHTML = serverResponse.message;
    } else {
        document.getElementById("login_error").innerHTML = '';
        localStorage.setItem('token', serverResponse.data);
        displayView();
    }
};


passwordMatch = function (first_password_id, second_password_id) {
    var password1 = document.getElementById(first_password_id);
    var password2 = document.getElementById(second_password_id);
    if (password1.value !== password2.value) {
        password2.setCustomValidity('Passwords does not match.');
    } else {
        password2.setCustomValidity('');
    }
};


passwordLength = function (password_id) {
    var password1 = document.getElementById(password_id).value;
    if (password1.length < 8) {
        document.getElementById(password_id).setCustomValidity('Password need to be at least 8 characters.');
    } else {
        document.getElementById(password_id).setCustomValidity('');
    }
};

resetValidation = function () {
    document.getElementById('signup_email').setCustomValidity('');
};


registerUser = function (event) {
    event.preventDefault();
    var signup_form = document.getElementById("signup_form");
    var email = signup_form.elements["email"];
    var password = signup_form.elements["password"];
    var firstname = signup_form.elements["first_name"];
    var familyname = signup_form.elements["family_name"];
    var gender = signup_form.elements["gender"];
    var city = signup_form.elements["city"];
    var country = signup_form.elements["country"];
    var dataObject = {
        email: email.value,
        password: password.value,
        firstname: firstname.value,
        familyname: familyname.value,
        gender: gender.value,
        city: city.value,
        country: country.value
    };
    var serverResponse = serverstub.signUp(dataObject);
    if (!serverResponse.success) {
        email.setCustomValidity(serverResponse.message);
    } else {
        email.setCustomValidity('');
        var signInResponse = serverstub.signIn(dataObject.email, dataObject.password);
        localStorage.setItem('token', signInResponse.data);
        displayView();
    }
};
