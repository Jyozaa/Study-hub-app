function searchuserfunc() {
    const query = document.getElementById("searchid").value;

    if (query.trim() !== "") {
        $.ajax({
            url: `/search_users?query=${encodeURIComponent(query)}`, 
            type: "GET",
            dataType: "json",
            success: function (data) {
                const resultsDiv = document.getElementById("searchresult");
                resultsDiv.innerHTML = "";

                if (data.users.length > 0) {
                    data.users.forEach(user => {
                        resultsDiv.innerHTML += `
                            <div class="card my-2">
                                <div class="card-body">
                                    <h5>${user.username}</h5>
                                    <p>Level: ${user.level}</p>
                                    <p>Total Study Time: ${Math.floor(user.total_study_time / 3600)} hours ${Math.floor(user.total_study_time / 60)} minutes</p>
                                    <a href="/user/${user.id}" class="btn btn-primary">View Profile</a>
                                </div>
                            </div>
                        `;
                    });
                } 
                else {
                    resultsDiv.innerHTML = `
                        <div class="card my-2">
                            <div class="card-body">
                                <h5>No user found.</h5>
                            </div>
                        </div>
                    `;
                }

            },
            error: function(){
                const resultsDiv = document.getElementById("searchresult");
                resultsDiv.innerHTML = `
                    <div class="alert alert-danger" role="alert">
                        Unable to fetch results. Please try again later.
                    </div>
                `;
            }
        });
    } else{
        document.getElementById("searchresult").innerHTML = "";
    }
}