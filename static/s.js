const promptElement = document.querySelector(".chat-prompt");
promptElement.classList.add("active");

// <!-- <script>

// document.getElementById("inputForm").addEventListener("submit", function (event) {
//     event.preventDefault(); 
//     const userInput = document.getElementById("textInput").value;
//     console.log(userInput)
//     // Clear the text input field for the next interaction
//     document.getElementById("textInput").value = "";
// });
// </script> -->

// document.getElementById("inputForm").addEventListener("submit", function (event) {
//     event.preventDefault();

//     const userInput = document.getElementById("textInput").value;
//     console.log(userInput);

//     // // Use AJAX to send a POST request to the server
//     // $.ajax({
//     //     url: '/',
//     //     method: 'POST',
//     //     data: { user_input: userInput },
//     //     success: function (data) {
//     //         // Update the page content without a full page reload
//     //         $('.chat-prompt').text(data.model_output);
//     //     },
//     //     error: function () {
//     //         console.error('Error in AJAX request');
//     //     }
//     // });

//     // Clear the text input field for the next interaction
//     // document.getElementById("textInput").value = "";
// });