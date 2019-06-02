/* Client web socket */
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



/* Chooses which page to show */
displayView = function () {
    if (localStorage.getItem("token") === null) {
        document.getElementById("view").innerHTML = document.getElementById("welcomeview").innerHTML;

        /* EventListeners */
        document.getElementById('login_form').addEventListener('submit', logIn);
        document.getElementById('signup_form').addEventListener('submit', registerUser);
        document.getElementById('email_field').addEventListener('input', resetValidation);

        //Validator password length and match.
        document.getElementById('password_field').addEventListener('input',
            function () {
                pwdLength('password_field')
            });
        document.getElementById('repeat_password_field').addEventListener('input',
            function () {
                pwdMatch('password_field', 'repeat_password_field')
            });
    } else {
        //Opens profile view at start tab and loads profile data from server.
        document.getElementById("view").innerHTML = document.getElementById("profileview").innerHTML;
        getUserData();
        updateMessageWall('start_msg_wall');
        /* EventListeners */
        document.getElementById('start_tab_btn').addEventListener('click', function(ev){showPage(ev, 'start_tab')});
        document.getElementById('browse_tab_btn').addEventListener('click', function(ev){showPage(ev, 'browse_tab')});
        document.getElementById('account_tab_btn').addEventListener('click', function(ev){showPage(ev, 'account_tab')});

        document.getElementById('start_msg_btn').addEventListener('click',
            function () {
                publishMessage('text_box', 'info_email', 'start_msg_wall')
            });
        document.getElementById("browse_user").addEventListener('submit', searchForUser);
        document.getElementById('browse_msg_btn').addEventListener('click',
            function () {
                publishMessage('browse_text_box', 'user_email', 'browse_msg_wall')
            });
        document.getElementById('browse_reload_btn').addEventListener('click',
            function () {
                updateMessageWall('browse_msg_wall')
            });
        document.getElementById('start_reload_btn').addEventListener('click',
            function () {
                updateMessageWall('start_msg_wall')
            });
        document.getElementById('change_password').addEventListener('submit', new_password);
        //Validator password length and match.
        document.getElementById('change_password1').addEventListener('input',
            function () {
                pwdLength('change_password1')
            });
        document.getElementById('change_password2').addEventListener('input',
            function () {
                pwdMatch('change_password1', 'change_password2')
            });
        document.getElementById('sign_out').addEventListener('submit', sign_out);

        // Opens start tab
        document.getElementById("start_tab_btn").click();
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
    tablinks = document.getElementsByClassName('tablinks');
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
    var params = 'token='+ token;
    //Request server
    var xhr = new XMLHttpRequest();
    xhr.open('GET', 'http://127.0.0.1:5000/home/get_user_data_by_token'+'?'+params, true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) {
            var returnObject = JSON.parse(xhr.responseText);
            if (returnObject.success) {
                var returnData = returnObject.data;
                var name = returnData.firstname;
                var family_name = returnData.familyname;
                var email = returnData.email;
                var gender = returnData.gender;
                var city = returnData.city;
                var country = returnData.country;
                document.getElementById('info_name').innerText = name + " " + family_name;
                document.getElementById('info_email').innerText = email;
                document.getElementById('info_gender').innerText = gender;
                document.getElementById('info_city').innerText = city;
                document.getElementById('info_country').innerText = country;
            }else {
                //Do nothing??
            }
        }
    };
    xhr.send();
};

publishMessage = function (text_input, receiver_email, msg_wall) {
    var message = document.getElementById(text_input).value;
    var token = localStorage.getItem('token');
    var email = document.getElementById(receiver_email).innerText;
    //Request server
    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://127.0.0.1:5000/post_message', true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) {
            updateMessageWall(msg_wall);
        }
    };
    var json_input = JSON.stringify({'token': token, 'email': email, 'message': message});
    xhr.send(json_input);
};

updateMessageWall = function (msg_wall) {
    document.getElementById(msg_wall).innerHTML = "";
    var token = localStorage.getItem('token');
    var url, params;
    if(msg_wall === 'browse_msg_wall'){
        var email = document.getElementById('user_email').innerText;
        url = 'http://127.0.0.1:5000/browse/get_user_messages_by_email';
        params = "token=" + token + '&' + "email=" + email;
    }else{
        url = 'http://127.0.0.1:5000/home/get_user_messages_by_token';
        params = "token=" + token;
    }
     //Request server
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url+'?'+params, true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) {
            var returnObject = JSON.parse(xhr.responseText);
            if (!returnObject.success) {
                // Do nothing.
            }else {
                var messageArray = returnObject.data;
                var i;
                for (i = messageArray.length-1; i >= 0 ; i--) {
                    var writer = messageArray[i].writer;
                    var content = messageArray[i].content;
                    document.getElementById(msg_wall).innerHTML += "<textarea readonly class='message_on_wall'>" + writer +
                        ": " + content + "</textarea>";
                }
            }
        }
    };
    xhr.send();
};

/* Browse panel */

/* Retrieves profile information about the user and its message wall. */
searchForUser = function (event) {
    event.preventDefault();
    document.getElementById('browse_error').innerText = "";
    var token = localStorage.getItem('token');
    var browse_email = document.getElementById('browse_email').value;
    var params = 'token=' + token + '&' + 'email=' + browse_email;
    //Request server
    var xhr = new XMLHttpRequest();
    xhr.open('GET', 'http://127.0.0.1:5000/browse/get_user_data_by_email'+'?'+params, true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) {
            var returnObject = JSON.parse(xhr.responseText);
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
                updateMessageWall('browse_msg_wall');
                document.getElementById('browse_profile').style.display = "block";
            }else{
                document.getElementById('browse_profile').style.display = "none";
                document.getElementById('browse_error').innerText = returnObject.message;
            }
        }
    };
    xhr.send();
};

/* Account panel */

sign_out = function (event) {
    event.preventDefault();
    //Request server
    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://127.0.0.1:5000/account/sign_out', true);
    xhr.setRequestHeader('Content-type', 'application/json');
    var json_input = JSON.stringify({"token": localStorage.getItem('token')});
    xhr.send(json_input);
    localStorage.removeItem("token");
    displayView();
};

new_password = function (event) {
    event.preventDefault();
    var old_password = document.getElementById("old_password").value;
    var new_password = document.getElementById("change_password1").value;
    var token = localStorage.getItem("token");
    //Request server
    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://127.0.0.1:5000/account/change_password', true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) {
            var returnObject = JSON.parse(xhr.responseText);
            document.getElementById("pwd_change_feedback").innerHTML = returnObject.message;
            if (!returnObject.success) {
                // Do nothing
            }else {
                document.getElementById('old_password').value = '';
                document.getElementById('change_password1').value = '';
                document.getElementById('change_password2').value = '';
            }
        }
    };
    var json_input = JSON.stringify({'token': token, 'oldPassword': old_password, 'newPassword': new_password});
    xhr.send(json_input);
};

/* Login functionality */
logIn = function (event) {
    event.preventDefault();
    var login_email = document.getElementById('login_email').value;
    var login_password = document.getElementById('login_password').value;
    //Request server
    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://127.0.0.1:5000/sign_in', true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) {
            var returnObject = JSON.parse(xhr.responseText);
            if (!returnObject.success) {
                document.getElementById("badLogin").innerHTML = returnObject.message;
            }else {
                document.getElementById("badLogin").innerHTML = '';
                localStorage.setItem('token', returnObject.data);
                connectWebsocket(login_email.toString());
                displayView();
            }
        }
    };
    var json_input = JSON.stringify({'email': login_email, 'password': login_password});
    xhr.send(json_input);
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
    document.getElementById('email_field').setCustomValidity('');
};

/* Tries to register a user. If it works it also logs in the user. */
registerUser = function (event) {
    event.preventDefault();
    var email = document.getElementById('email_field');
    var password = document.getElementById('password_field');
    var firstname = document.getElementById('first_name_field');
    var familyname = document.getElementById('family_name_field');
    var gender = document.getElementById('gender');
    var city = document.getElementById('city_field');
    var country = document.getElementById('country_field');
    var input = {
        email: email.value,
        password: password.value,
        firstname: firstname.value,
        familyname: familyname.value,
        gender: gender.value,
        city: city.value,
        country: country.value
    };
    var json_input = JSON.stringify(input);
    //Request server
    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://127.0.0.1:5000/sign_up', true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) {
            var returnObject = JSON.parse(xhr.responseText);
            if (!returnObject.success) {
                email.setCustomValidity(returnObject.message);
            }else {
                email.setCustomValidity('');
                //TODO: ADD MESSAGE OF SUCCESS.
                document.getElementById("signup_form").reset();
                displayView();
            }
        }
    };
    xhr.send(json_input);
};
