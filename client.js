/* Chooses which page to show */
displayView = function () {
    if (localStorage.getItem("token") === null) {
        document.getElementById("view").innerHTML = document.getElementById("welcomeview").innerHTML;

        /* EventListeners */
        document.getElementById('login_form').addEventListener('submit', logIn);
        document.getElementById('signup_form').addEventListener('submit', registerUser);
        document.getElementById('signup_email').addEventListener('input', resetValidation);

        //Validator password length and match.
        document.getElementById('signup_password').addEventListener('input',
            function () {
                pwdLength('signup_password')
            });
        document.getElementById('repeat_password').addEventListener('input',
            function () {
                pwdMatch('signup_password', 'repeat_password')
            });
    } else {
        //Opens profile view at start tab and loads profile data from server.
        document.getElementById("view").innerHTML = document.getElementById("profileview").innerHTML;
        getUserData();
        updateWall('message_wall');
        /* EventListeners */
        document.getElementById('home_tab_btn').addEventListener('click', function(ev){showPage(ev, 'home_tab')});
        document.getElementById('browse_tab_btn').addEventListener('click', function(ev){showPage(ev, 'browse_tab')});
        document.getElementById('account_tab_btn').addEventListener('click', function(ev){showPage(ev, 'account_tab')});

        document.getElementById('message_button').addEventListener('click',
            function () {
                publishMessage('message_box', 'email_info', 'message_wall')
            });
        document.getElementById("browse_user").addEventListener('submit', searchForUser);
        document.getElementById('send_browse_msg').addEventListener('click',
            function () {
                publishMessage('browse_message', 'user_email', 'browse_message_wall')
            });
        document.getElementById('reload_browse_wall_btn').addEventListener('click',
            function () {
                updateWall('browse_message_wall')
            });
        document.getElementById('reload_wall_button').addEventListener('click',
            function () {
                updateWall('message_wall')
            });
        document.getElementById('password_change').addEventListener('submit', new_password);
        //Validator password length and match.
        document.getElementById('new_password').addEventListener('input',
            function () {
                pwdLength('new_password')
            });
        document.getElementById('confirm_new_pw').addEventListener('input',
            function () {
                pwdMatch('new_password', 'confirm_new_pw')
            });
        document.getElementById('sign_out').addEventListener('submit', sign_out);

        // Opens start tab
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

/* Tab functionality */
showPage = function (evt, tab) {
    var i, content, tablinks;
    //Hides all pages to begin with.
    content = document.getElementsByClassName('tab_content');
    for (i = 0; i < content.length; i++) {
        content[i].style.display = "none";
    }

    //set all tabs inactive
    tablinks = document.getElementsByClassName('tab_button');
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    document.getElementById(tab).style.display = "block";
    evt.currentTarget.className += " active";
};

/* Start panel */

/* Retrieves profile information for start page */
getUserData = function () {
    var token = localStorage.getItem('token');
    var returnObject = serverstub.getUserDataByToken(token).data;
    var name = returnObject.firstname;
    var family_name = returnObject.familyname;
    var email = returnObject.email;
    var gender = returnObject.gender;
    var city = returnObject.city;
    var country = returnObject.country;

    document.getElementById('name_info').innerText = name + " " + family_name;
    document.getElementById('email_info').innerText = email;
    document.getElementById('gender_info').innerText = gender;
    document.getElementById('city_info').innerText = city;
    document.getElementById('country_info').innerText = country;

};


publishMessage = function (text_input, receiver_email, msg_wall) {
    var message = document.getElementById(text_input).value;
    var token = localStorage.getItem('token');
    var email = document.getElementById(receiver_email).innerText;
    console.log(message, token, email);
    serverstub.postMessage(token, message, email);
    updateWall(msg_wall);
};

updateWall = function (msg_wall) {
    document.getElementById(msg_wall).innerHTML = "";
    var token = localStorage.getItem('token');
    var messageArray;
    if (msg_wall === 'browse_message_wall'){
        var email = document.getElementById('user_email').innerText;
        messageArray = serverstub.getUserMessagesByEmail(token, email).data
    }else {
        messageArray = serverstub.getUserMessagesByToken(token).data;
    }
    console.log(messageArray);
    var i;
    for (i = 0; i < messageArray.length; i++) {
        var writer = messageArray[i].writer;
        var content = messageArray[i].content;
        document.getElementById(msg_wall).innerHTML += "<textarea readonly class='message_on_wall'>" + writer +
            ": " + content + "</textarea>";
    }
};


/* Browse panel */

/* Retrieves profile information about the user and its message wall. */
searchForUser = function (event) {
    event.preventDefault();
    document.getElementById('user_not_found').innerText = "";
    var token = localStorage.getItem('token');
    var browse_email = document.getElementById('search_email').value;
    var returnObject = serverstub.getUserDataByEmail(token, browse_email);

    if (returnObject.success) {
        var name = returnObject.data.firstname;
        var family_name = returnObject.data.familyname;
        var email = returnObject.data.email;
        var gender = returnObject.data.gender;
        var city = returnObject.data.city;
        var country = returnObject.data.country;
        document.getElementById('user_name').innerText = name + " " + family_name;
        document.getElementById('user_email').innerText = email;
        document.getElementById('user_gender').innerText = gender;
        document.getElementById('user_city').innerText = city;
        document.getElementById('user_country').innerText = country;
        updateWall('browse_message_wall');
        document.getElementById('user_profile').style.display = "block";
    } else {
        document.getElementById('user_profile').style.display = "none";
        document.getElementById('user_not_found').innerText = returnObject.message;
    }
};

/* Account panel */

sign_out = function (event) {
    event.preventDefault();
    serverstub.signOut(localStorage.getItem("token"));
    localStorage.removeItem("token");
    displayView();
};


new_password = function (event) {
    event.preventDefault();
    var old_password = document.getElementById("old_password").value;
    var new_password = document.getElementById("new_password").value;
    var returnObject = serverstub.changePassword(localStorage.getItem("token"), old_password, new_password);
    document.getElementById("new_pwd_feedback").innerHTML = returnObject.message;
    if (!returnObject.success) {
    } else {
        document.getElementById('old_password').value = '';
        document.getElementById('new_password').value = '';
        document.getElementById('confirm_new_pw').value = '';
    }
};

/* Login functionality */
logIn = function (event) {
    event.preventDefault();
    var login_email = document.getElementById('login_email');
    var login_password = document.getElementById('login_password');
    var returnObject = serverstub.signIn(login_email.value, login_password.value);
    if (!returnObject.success) {
        document.getElementById("login_error").innerHTML = returnObject.message;
    } else {
        document.getElementById("login_error").innerHTML = '';
        localStorage.setItem('token', returnObject.data);
        displayView();
    }
};


/* Validates that two passwords match. */
pwdMatch = function (first_password_id, second_password_id) {
    var password1 = document.getElementById(first_password_id);
    var password2 = document.getElementById(second_password_id);
    if (password1.value !== password2.value) {
        password2.setCustomValidity('Passwords does not match.');
    } else {
        password2.setCustomValidity('');
    }
};

/* Validates that the password is long enough */
pwdLength = function (password_id) {
    var password1 = document.getElementById(password_id).value;
    if (password1.length < 8) {
        document.getElementById(password_id).setCustomValidity('Password need to be at least 8 characters.');
    } else {
        document.getElementById(password_id).setCustomValidity('');
    }
};

/* Resets the custom validity if email was already registered. */
resetValidation = function () {
    document.getElementById('signup_email').setCustomValidity('');
};

/* Tries to register a user. If it works it also logs in the user. */
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
    var returnedObject = serverstub.signUp(dataObject);
    if (!returnedObject.success) {
        email.setCustomValidity(returnedObject.message);
    } else {
        email.setCustomValidity('');
        var signInResponse = serverstub.signIn(dataObject.email, dataObject.password);
        localStorage.setItem('token', signInResponse.data);
        displayView();
    }
};
