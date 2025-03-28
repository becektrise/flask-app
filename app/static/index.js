function deleteMovie(movieId) {
  fetch("/delete_movie", {
    method: "POST",
    body: JSON.stringify({ movieId: movieId }),
  }).then((_res) => {
    window.location.href = "/database";
  });
}
