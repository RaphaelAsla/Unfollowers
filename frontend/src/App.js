import React, { useState } from "react";
import "./App.css";

function App() {
	const [sessionId, setSessionId] = useState("");
	const [username, setUsername] = useState("");
	const [password, setPassword] = useState("");
	const [isLoading, setIsLoading] = useState(false);
	const [profilesList, setProfilesList] = useState([]);
	const [isLoginMode, setIsLoginMode] = useState(false);

	const handleSubmit = (event) => {
		event.preventDefault();
		setIsLoading(true);

		const body = isLoginMode
			? { username: username, password: password }
			: { session_id: sessionId };

		const api_url = isLoginMode ? "http://127.0.0.1:8000/api/v2/data" : "http://127.0.0.1:8000/api/v1/data";

		fetch(api_url, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify(body),
		})
			.then(response => response.json())
			.then(data => {
				if (data && typeof data === "object") {
					const profiles = Object.keys(data).map(name => ({
						name,
						small_name: data[name]["full_name"],
						profilePic: data[name]["profile_pic_url"],
					}));
					setProfilesList(profiles);
				} else {
					setProfilesList([]);
				}
				setIsLoading(false);
			})
			.catch(error => {
				console.error("Error:", error);
				setIsLoading(false);
				setProfilesList([]);
			});

		setSessionId("");
		setUsername("");
		setPassword("");
	};

	return (
		<div className="App">
			<header className="App-header">
				<h1 className="App-title">Unfollowers</h1>
				<form onSubmit={handleSubmit}>
					{isLoginMode ? (
						<>
							<label>
								<input
									type="text"
									value={username}
									onChange={(e) => setUsername(e.target.value)}
									placeholder="Phone, username, or email"
									className="username-input"
									required
								/>
							</label>
							<label>
								<input
									type="password"
									value={password}
									onChange={(e) => setPassword(e.target.value)}
									placeholder="Password"
									className="password-input"
									required
								/>
							</label>
						</>
					) : (
						<label>
							<input
								type="text"
								value={sessionId}
								onChange={(e) => setSessionId(e.target.value)}
								placeholder="SessionID"
								className="session-input"
								required
							/>
						</label>
					)}
					<div className="buttons-container">
						{isLoading ? (
							<div className="loading-text">Loading...</div>
						) : (
							<>
								<button type="submit">
									Submit
								</button>
								<button onClick={(e) => {
									e.preventDefault();
									setIsLoginMode(!isLoginMode);
								}}>
									{isLoginMode ? "Use SessionID" : "Use Credentials"}
								</button>
							</>
						)}
					</div>
				</form>

				{profilesList.length > 0 && (
					<div className="profiles-list-container">
						{profilesList.map((profile, index) => (
							<div key={index} className="rounded-box">
								<img
									src={`http://127.0.0.1:8000/proxy?url=${encodeURIComponent(profile.profilePic)}`}
									alt={`${profile.name}'s profile`}
									className="profile-pic"
								/>
								<div className="profile-info">
									<div className="name">{profile.name}</div>
									<div className="small-name">{profile.small_name}</div>
								</div>
							</div>
						))}
					</div>
				)}
			</header>
		</div>
	);
}

export default App;
