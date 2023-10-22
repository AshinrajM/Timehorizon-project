function copyToClipboard(id) {
    var inputId = 'couponCodeInput_' + id;
    var input = document.getElementById(inputId);
    // var input2 = document.getElementById("");
    console.log(input);

    if (input) {
        // Select the input text
        input.select();
        input.setSelectionRange(0, 99999); // For mobile devices

        // Copy the text to the clipboard
        document.execCommand("copy");

        // Deselect the input field
        input.blur();

        // Optionally, you can provide feedback to the user
        // alert("Coupon code copied to clipboard: " + input.value);
    }

}