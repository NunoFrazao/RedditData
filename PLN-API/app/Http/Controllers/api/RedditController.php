<?php

namespace App\Http\Controllers\api;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use App\Http\Controllers\Controller;
use Illuminate\Support\Facades\Http;
use Symfony\Component\Process\Process;
use Symfony\Component\Process\Exception\ProcessFailedException;

use App\Models\Like;
use App\Http\Resources\LikeResource;

class RedditController extends Controller
{
    private $clientId = '<CLIENT_ID>';
    private $clientSecret = '<CLIENT_SECRET>';
    private $redditUserAgent = 'PLN Test/0.1 by PLN_user1';

    public function getAccessToken()
    {
        $username = 'PLN_user1'; // Hardcoded username
        $password = 'plnteste'; // Hardcoded password

        $response = Http::asForm()->withBasicAuth($this->clientId, $this->clientSecret)
            ->withHeaders(['User-Agent' => $this->redditUserAgent])
            ->post('https://www.reddit.com/api/v1/access_token', [
                'grant_type' => 'password',
                'username' => $username,
                'password' => $password
            ]);

        return response()->json($response->json(), $response->status());
    }

    public function getData(Request $request)
    {
        $data = $request->json()->all();
        $dataPath = base_path('pythonProject4/data.txt');

        try {
            file_put_contents($dataPath, json_encode(['data' => $data], JSON_PRETTY_PRINT));
            return response()->json(['message' => 'Data saved successfully'], 200);
        } catch (\Exception $e) {
            Log::error("Failed to save data: " . $e->getMessage());
            return response()->json(['message' => 'Failed to save data'], 500);
        }
    }

    public function analyzeData()
    {
        $filePath = base_path('pythonProject4/data.txt');

        if (!file_exists($filePath)) {
            return response()->json(['message' => 'Data file not found'], 404);
        }

        // Determine the correct activation script based on the operating system
        $venvActivatePath = '';
        if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
            $venvActivatePath = base_path('.venv/Scripts/activate.bat'); // For Windows
        } else {
            $venvActivatePath = base_path('.venv/bin/activate'); // For Unix-like systems
        }

        $pythonScriptPath = base_path('pythonProject4/main.py');

        // Construct the command to activate the virtual environment and run the script
        if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
            // For Windows, we need to chain commands using && within cmd.exe
            $command = "cmd.exe /c \"{$venvActivatePath} && python {$pythonScriptPath}\"";
        } else {
            $command = "source {$venvActivatePath} && python {$pythonScriptPath}";
        }

        // Execute the command
        $process = Process::fromShellCommandline($command);
        $process->setWorkingDirectory(base_path('pythonProject4'));

        try {
            Log::info("Running Python script...");
            $process->mustRun();
            Log::info("Python script output: " . $process->getOutput());

            $analyzedDataPath = base_path('pythonProject4/analyzed_data.txt');
            if (file_exists($analyzedDataPath)) {
                $analyzedData = json_decode(file_get_contents($analyzedDataPath), true);
                return response()->json($analyzedData, 200);
            } else {
                return response()->json(['message' => 'Analyzed data not found'], 500);
            }
        } catch (ProcessFailedException $exception) {
            Log::error("Python script failed: " . $exception->getMessage());
            return response()->json(['message' => 'Failed to analyze data'], 500);
        }
    }

    public function analyzeDataVader()
    {
        Log::info("Analyzing data using VADER sentiment analysis...");

        $filePath = base_path('pythonProject4/data.txt');

        if (!file_exists($filePath)) {
            Log::error("Data file not found: " . $filePath);
            return response()->json(['message' => 'Data file not found'], 404);
        }

        // Determine the correct activation script based on the operating system
        $venvActivatePath = '';
        if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
            $venvActivatePath = base_path('.venv/Scripts/activate.bat'); // For Windows
        } else {
            $venvActivatePath = base_path('.venv/bin/activate'); // For Unix-like systems
        }

        $pythonScriptPath = base_path('pythonProject4/main_vader.py');

        // Construct the command to activate the virtual environment and run the script
        if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
            // For Windows, we need to chain commands using && within cmd.exe
            $command = "cmd.exe /c \"{$venvActivatePath} && python {$pythonScriptPath}\"";
        } else {
            $command = "source {$venvActivatePath} && python {$pythonScriptPath}";
        }

        // Execute the command
        $process = Process::fromShellCommandline($command);
        $process->setWorkingDirectory(base_path('pythonProject4'));

        try {
            Log::info("Running Python script for VADER analysis...");
            Log::info("Command: " . $command);
            $process->mustRun();
            Log::info("Python script output: " . $process->getOutput());

            $analyzedDataPath = base_path('pythonProject4/analyzed_data.txt');
            if (file_exists($analyzedDataPath)) {
                $analyzedData = json_decode(file_get_contents($analyzedDataPath), true);
                return response()->json($analyzedData, 200);
            } else {
                Log::error("Analyzed data file not found: " . $analyzedDataPath);
                return response()->json(['message' => 'Analyzed data not found'], 500);
            }
        } catch (ProcessFailedException $exception) {
            Log::error("Python script for VADER analysis failed: " . $exception->getMessage());
            return response()->json(['message' => 'Failed to analyze data'], 500);
        } catch (\Exception $e) {
            Log::error("Unexpected error during VADER analysis: " . $e->getMessage());
            return response()->json(['message' => 'Unexpected error occurred'], 500);
        }
    }

    public function getComments($postId, Request $request)
    {
        try {
            $accessToken = $request->bearerToken(); // Get the bearer token from the request

            $response = Http::withHeaders([
                'Authorization' => 'Bearer ' . $accessToken,
                'User-Agent' => $this->redditUserAgent
            ])->get("https://oauth.reddit.com/comments/{$postId}");

            if ($response->successful()) {
                $data = $response->json();

                // Check if the data structure is as expected
                if (!isset($data[1]['data']['children'])) {
                    return response()->json(['message' => 'Failed to fetch comments due to unexpected data structure'], 500);
                }

                // Process comments data to fit your needs
                $comments = [];
                $count = 0;
                foreach ($data[1]['data']['children'] as $comment) {
                    if ($comment['kind'] === 't1') { // Ensure it's a comment
                        $comments[] = [
                            'id' => $comment['data']['id'],
                            'body' => $comment['data']['body']
                        ];
                        $count++;
                    }
                    if ($count >= 10) { // Limit the number of comments to 10
                        break;
                    }
                }

                // Save the comments data to comments_data.txt file
                $commentsFilePath = base_path('pythonProject4/comments_data.txt');
                file_put_contents($commentsFilePath, json_encode($comments));

                return response()->json(['message' => 'Comments data saved successfully'], 200);
            } else {
                Log::error('Failed to fetch comments', [
                    'status' => $response->status(),
                    'response' => $response->body()
                ]);
                return response()->json(['message' => 'Failed to fetch comments'], $response->status());
            }
        } catch (\Exception $e) {
            Log::error('Exception when fetching comments', [
                'exception' => $e->getMessage()
            ]);
            return response()->json(['message' => 'Failed to fetch comments'], 500);
        }
    }

    // Add the new analyzeComments method
    public function analyzeComments()
    {
        $filePath = base_path('pythonProject4/comments_data.txt');

        if (!file_exists($filePath)) {
            return response()->json(['message' => 'Comments data file not found'], 404);
        }

        // Determine the correct activation script based on the operating system
        $venvActivatePath = '';
        if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
            $venvActivatePath = base_path('.venv/Scripts/activate.bat'); // For Windows
        } else {
            $venvActivatePath = base_path('.venv/bin/activate'); // For Unix-like systems
        }

        $pythonScriptPath = base_path('pythonProject4/analyze_comments.py');

        // Construct the command to activate the virtual environment and run the script
        if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
            // For Windows, we need to chain commands using && within cmd.exe
            $command = "cmd.exe /c \"{$venvActivatePath} && python {$pythonScriptPath}\"";
        } else {
            $command = "source {$venvActivatePath} && python {$pythonScriptPath}";
        }

        // Execute the command
        $process = Process::fromShellCommandline($command);
        $process->setWorkingDirectory(base_path('pythonProject4'));

        try {
            Log::info("Running Python script for comments...");
            $process->mustRun();
            Log::info("Python script for comments output: " . $process->getOutput());

            $analyzedCommentsPath = base_path('pythonProject4/analyzed_comments_data.txt');
            if (file_exists($analyzedCommentsPath)) {
                $analyzedComments = json_decode(file_get_contents($analyzedCommentsPath), true);
                return response()->json($analyzedComments, 200);
            } else {
                return response()->json(['message' => 'Analyzed comments data not found'], 500);
            }
        } catch (ProcessFailedException $exception) {
            Log::error("Python script for comments failed: " . $exception->getMessage());
            return response()->json(['message' => 'Failed to analyze comments data'], 500);
        }
    }

    public function getUserLikesAndPosts(Request $request, $userId)
    {
        // Fetch likes for the user
        $likes = Like::where('user_id', $userId)->get();
        $postIds = $likes->pluck('post_id')->all();

        // Load posts details from the local file
        $filePath = base_path('pythonProject4/analyzed_data_cache.txt');
        $postsFromFile = json_decode(file_get_contents($filePath), true);

        // Convert posts to an associative array for quick lookup
        $postsDetails = [];
        foreach ($postsFromFile as $post) {
            $postsDetails[$post['id']] = $post;
        }

        // Combine the likes with post details
        $likesWithPosts = $likes->map(function ($like) use ($postsDetails) {
            $postId = $like->post_id;
            return [
                'like' => new LikeResource($like),
                'post' => $postsDetails[$postId] ?? null // Safeguard against null entries
            ];
        });

        return response()->json($likesWithPosts);
    }

    // Add this method in RedditController
    public function getLikesDislikes(Request $request)
    {
        $postIds = $request->input('post_ids', []);

        if (empty($postIds)) {
            return response()->json(['message' => 'No post IDs provided'], 400);
        }

        // Fetch likes/dislikes from the database
        $likes = Like::whereIn('post_id', $postIds)->get();

        $likesDislikes = $likes->groupBy('post_id')->map(function ($likeGroup) {
            $likesCount = $likeGroup->where('like', 1)->count();
            $dislikesCount = $likeGroup->where('like', -1)->count();
            $userLike = optional($likeGroup->first())->like;

            return [
                'likes' => $likesCount,
                'dislikes' => $dislikesCount,
                'user_like' => $userLike
            ];
        });

        return response()->json($likesDislikes, 200);
    }

    public function analyze(Request $request)
    {
        /*
            Author: Leandro Vieira
            Module: 2
        */

        // Validação do JSON recebido
        $request->validate([
            'data' => 'required|array',
        ]);

        $data = $request->input('data');

        try {
            // Envia o JSON para o serviço Python e recebe a resposta
            $response = Http::post('http://localhost:8081/analyze', [
                'data' => $data,
            ]);

            if ($response->successful()) {
                $newAnalyzedData = $response->json();

                // Load existing cache data
                $cacheFilePath = base_path('pythonProject4/analyzed_data_cache.txt');
                $existingData = [];
                if (file_exists($cacheFilePath)) {
                    $existingData = json_decode(file_get_contents($cacheFilePath), true);
                }

                // Append the new analyzed data
                $updatedData = array_merge($existingData, $newAnalyzedData);

                // Save the updated data back to the cache file
                file_put_contents($cacheFilePath, json_encode($updatedData, JSON_PRETTY_PRINT));

                return response()->json($newAnalyzedData);
            } else {
                return response()->json(['error' => 'Failed to analyze data'], $response->status());
            }
        } catch (\Exception $e) {
            return response()->json(['error' => 'Failed to connect to the script service'], 500);
        }
    }

    public function analyzeVader(Request $request)
    {
        /*
            Author: Leandro Vieira
            Module: 2
        */

        // Validação do JSON recebido
        $request->validate([
            'data' => 'required|array',
        ]);

        $data = $request->input('data');

        try {
            // Envia o JSON para o serviço Python e recebe a resposta
            $response = Http::post('http://localhost:8081/analyze/vader', [
                'data' => $data,
            ]);

            if ($response->successful()) {
                $newAnalyzedData = $response->json();

                // Load existing cache data
                $cacheFilePath = base_path('pythonProject4/analyzed_data_cache.txt');
                $existingData = [];
                if (file_exists($cacheFilePath)) {
                    $existingData = json_decode(file_get_contents($cacheFilePath), true);
                }

                // Append the new analyzed data
                $updatedData = array_merge($existingData, $newAnalyzedData);

                // Save the updated data back to the cache file
                file_put_contents($cacheFilePath, json_encode($updatedData, JSON_PRETTY_PRINT));

                return response()->json($newAnalyzedData);
            } else {
                return response()->json(['error' => 'Failed to analyze data'], $response->status());
            }
        } catch (\Exception $e) {
            return response()->json(['error' => 'Failed to connect to the script service'], 500);
        }
    }
}
