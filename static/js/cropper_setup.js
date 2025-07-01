// static/js/cropper_setup.js

document.addEventListener("DOMContentLoaded", function () {
  let cropper;
  const imageToCrop = document.getElementById("imageToCrop"); // The <img> tag in the modal
  const imageInput = document.getElementById("image"); // The original file input
  const cropModalElement = document.getElementById("cropModal"); // Get the modal DOM element
  const cropModal = new bootstrap.Modal(cropModalElement); // Initialize Bootstrap Modal instance
  const cropAndSaveBtn = document.getElementById("cropAndSaveBtn");
  // const croppedImageInput = document.getElementById("croppedImageInput"); // This variable is unused and can be removed.
  const currentImagePreview = document.getElementById("currentImagePreview"); // For edit.html

  let hasCropped = false; // NEW: Flag to indicate if cropping was successful

  // Function to initialize or reset cropper
  function initCropper(imgElement) {
    if (cropper) {
      cropper.destroy();
    }
    cropper = new Cropper(imgElement, {
      aspectRatio: 1, // Enforce a square aspect ratio
      viewMode: 1, // Restrict the crop box to not exceed the canvas
      autoCropArea: 0.8, // Initial crop area (80% of image)
      movable: true,
      zoomable: true,
      rotatable: false,
      scalable: false,
      // preview: '.img-preview' // If you want a live preview elsewhere
    });
  }

  // Handle file input change event
  if (imageInput) {
    imageInput.addEventListener("change", function (e) {
      hasCropped = false; // Reset flag on new file selection
      const files = e.target.files;
      if (files && files.length > 0) {
        const file = files[0];
        if (file.type.startsWith("image/")) {
          const reader = new FileReader();
          reader.onload = function () {
            imageToCrop.src = reader.result;
            cropModal.show(); // Show the modal with the image
            // Delay cropper initialization until modal is fully shown and image is loaded
            imageToCrop.onload = () => {
              initCropper(imageToCrop);
            };
          };
          reader.readAsDataURL(file); // Read file as data URL for Cropper.js
        } else {
          alert("Please select an image file (png, jpg, jpeg, gif).");
          imageInput.value = ""; // Clear the input if not an image
        }
      }
    });
  }

  // Handle Crop and Save button click
  if (cropAndSaveBtn) {
    cropAndSaveBtn.addEventListener("click", function () {
      if (cropper) {
        // Get cropped canvas as a Blob (preferred for form submission)
        cropper
          .getCroppedCanvas({
            width: 400, // Desired output width
            height: 400, // Desired output height
            imageSmoothingEnabled: true,
            imageSmoothingQuality: "high",
          })
          .toBlob(
            function (blob) {
              // Create a File object from the blob, mimicking a file input
              const fileName = "cropped_image.png"; // You can use a more dynamic name
              const file = new File([blob], fileName, { type: blob.type });

              // Create a DataTransfer object and add the file
              const dataTransfer = new DataTransfer();
              dataTransfer.items.add(file);

              // Assign the DataTransfer.files to the original file input
              imageInput.files = dataTransfer.files;
              hasCropped = true; // NEW: Set flag to true on successful crop

              cropModal.hide(); // Hide the modal

              // Optional: Update a small preview on the main form
              if (currentImagePreview) {
                const reader = new FileReader();
                reader.onload = function (e) {
                  currentImagePreview.src = e.target.result;
                };
                reader.readAsDataURL(file);
              }
            },
            "image/png",
            0.9
          ); // Output as PNG with 90% quality
      }
    });
  }

  // Reset cropper when modal is hidden
  cropModalElement.addEventListener("hidden.bs.modal", function () {
    if (cropper) {
      cropper.destroy();
      imageToCrop.src = ""; // Clear image from modal

      // NEW: Only clear the imageInput.value if a crop was NOT performed
      if (!hasCropped) {
        imageInput.value = ""; // Clear the actual file input if user cancelled or didn't crop
      }
      hasCropped = false; // Reset flag for next interaction
    }
  });

  // For edit.html, if an image already exists, update the preview initially
  // No action needed for cropper initialization here, as cropper only works on new uploads.
  // The currentImagePreview will naturally show the existing image.
  // The logic here is fine.
});
