<!-- JavaScript for adding product to favorites -->
<script>
    function add_to_favorites(product_id) {
        // Send an AJAX request to add the product to favorites
        $.ajax({
            url: "{% url 'jersey_app:add_to_favorites' %}",
            method: "POST",
            data: {
                'product_id': product_id,
                'csrfmiddlewaretoken': '{{ csrf_token }}' // Include CSRF token for security
            },
            success: function(response) {
                // Handle success response
                console.log(response);
            },
            error: function(xhr, status, error) {
                // Handle error response
                console.error(xhr.responseText);
            }
        });
    }
</script>