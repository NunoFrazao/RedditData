<?php

namespace App\Http\Controllers\api;

use App\Models\User;
use Illuminate\Http\Request;
use App\Http\Controllers\Controller;
use App\Http\Resources\UserResource;
use App\Http\Requests\StoreUserRequest;
use App\Http\Requests\UpdateUserRequest;
use App\Models\Like;
use DateTime;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;

class UserController extends Controller
{
    public function index()
    {
        return UserResource::collection(User::all());
    }

    public function show(User $user)
    {
        return new UserResource($user);
    }

    public function store(StoreUserRequest $request)
    {
        $dataToSave = $request->validated();

        $user = new User();
        $user->name = $dataToSave['name'];
        $user->email = $dataToSave['email'];
        $user->password = bcrypt($dataToSave['password']);
        $user->tipo_user = $dataToSave['tipo_user'];
        $user->contacto = $dataToSave['contacto'];
        $user->save();
        return new UserResource($user);
    }

    public function update(UpdateUserRequest $request, User $user)
    {
        $dataToSave = $request->validated();

        $user->fill($dataToSave);
        $user->save();
        return new UserResource($user);
    }

    public function destroy(User $user)
    {
        // delete a user
        $user->delete();
        return new UserResource($user);
    }

    public function deleteAccount($id)
    {
        try {
            // Count the number of admins
            $adminCount = User::where('tipo_user', 1)->count();

            // Get the user trying to be deleted
            $user = User::findOrFail($id);

            // Check if the user is the last admin
            if ($user->tipo_user == 1 && $adminCount <= 1) {
                return response()->json(['error' => 'Cannot delete the last admin account'], 403);
            }

            // If not the last admin, proceed with deletion
            $user->delete();

            return response()->json(['message' => 'User deleted successfully']);
        } catch (\Exception $e) {
            Log::error('Error deleting user account: ' . $e->getMessage());
            return response()->json(['message' => 'Internal Server Error'], 500);
        }
    }

    public function getUserById($id)
    {
        $user = User::where('id', $id)->first();

        if ($user) {
            return new UserResource($user);
        } else {
            return response()->json(['error' => 'User not found'], 404);
        }
    }

    public function getUser(Request $request)
    {
        $user = User::where('email', $request->email)->first();

        if ($user && Hash::check($request->password, $user->password)) {
            return new UserResource($user);
        } else {
            return response()->json(['error' => 'Invalid credentials'], 401);
        }
    }

    public function storeHistory(Request $request)
    {
        $validatedData = $request->validate([
            'user_id' => 'required|exists:users,id',
            'query' => 'required|string|max:100',
            'tipo_pesquisa' => 'required|in:normal,topic,gpt,elastic'
        ]);

        DB::table('historico')->insert([
            'user_id' => $validatedData['user_id'],
            'query' => $validatedData['query'],
            'tipo_pesquisa' => $validatedData['tipo_pesquisa'],
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        return response()->json(['message' => 'Search history recorded successfully.']);
    }

    public function getHistoryByUserId($userId)
    {
        $history = DB::table('historico')->where('user_id', $userId)->get();
        return response()->json($history);
    }

    public function getPostsLikesDislikesHistory()
    {
        try {
            // Fetch likes and dislikes counts grouped by post_id
            $likesDislikes = Like::select(
                'post_id',
                DB::raw('SUM(CASE WHEN likes.like = 1 THEN 1 ELSE 0 END) as count_likes'),
                DB::raw('SUM(CASE WHEN likes.like = -1 THEN 1 ELSE 0 END) as count_dislikes')
            )
                ->groupBy('post_id')
                ->get();

            // Assuming you have a method to get the permalink based on post_id or that you handle it directly in the frontend
            $history = $likesDislikes->map(function ($likeDislike, $index) {
                return [
                    'id' => $index + 1, // Generate a unique ID for each entry, starting from 1
                    'post_id' => $likeDislike->post_id,
                    'count_likes' => $likeDislike->count_likes,
                    'count_dislikes' => $likeDislike->count_dislikes,
                    'permalink' => $this->getPermalink($likeDislike->post_id) // Assuming you have a method to get the permalink
                ];
            });

            return response()->json($history);
        } catch (\Exception $e) {
            Log::error('Error fetching posts likes/dislikes history: ' . $e->getMessage());
            return response()->json(['message' => 'Internal Server Error'], 500);
        }
    }

    // Example placeholder method for getting permalink based on post_id
    protected function getPermalink($postId)
    {
        // Construct the permalink here, or fetch it from wherever it is stored or generated
        return '/r/someSubreddit/comments/' . $postId;
    }

    public function getSearchesPerDay()
    {
        $currentMonth = now()->format('Y-m');
        $daysInMonth = now()->daysInMonth;
        $searchesPerDay = DB::table('historico')
            ->select(DB::raw('DATE(created_at) as date'), DB::raw('count(*) as count'))
            ->where('created_at', 'like', "$currentMonth%")
            ->groupBy('date')
            ->get()
            ->keyBy('date');

        $data = [];
        $labels = [];

        for ($day = 1; $day <= $daysInMonth; $day++) {
            $date = now()->format('Y-m-') . str_pad($day, 2, '0', STR_PAD_LEFT);
            $labels[] = $day . ' ' . now()->format('M'); // Format as "1 Aug", "2 Aug", etc.
            $data[] = $searchesPerDay->get($date)->count ?? 0; // Default to 0 if no searches
        }

        return response()->json([
            'labels' => $labels,
            'data' => $data,
        ]);
    }

    public function getUsersCountForComparison()
    {
        try {
            $twoMonthsAgo = now()->subMonths(1)->startOfMonth();
            $currentMonth = now()->startOfMonth();

            // Query to get the number of users registered in the last two months
            $usersLastTwoMonths = DB::table('users')
                ->select(DB::raw('DATE_FORMAT(created_at, "%Y-%m") as month'), DB::raw('count(*) as count'))
                ->whereBetween('created_at', [$twoMonthsAgo, now()])
                ->groupBy('month')
                ->get();

            $previousMonthCount = 0;
            $currentMonthCount = 0;

            foreach ($usersLastTwoMonths as $record) {
                if ($record->month == $twoMonthsAgo->format('Y-m')) {
                    $previousMonthCount = $record->count;
                } elseif ($record->month == $currentMonth->format('Y-m')) {
                    $currentMonthCount = $record->count;
                }
            }

            return response()->json([
                'currentMonthCount' => $currentMonthCount,
                'previousMonthCount' => $previousMonthCount,
            ]);
        } catch (\Exception $e) {
            Log::error('Error fetching user count for comparison: ' . $e->getMessage());
            return response()->json(['message' => 'Internal Server Error'], 500);
        }
    }

    public function getAdminCount()
    {
        try {
            // Count the number of admins
            $adminCount = User::where('tipo_user', 1)->count();

            return response()->json(['adminCount' => $adminCount]);
        } catch (\Exception $e) {
            Log::error('Error fetching admin count: ' . $e->getMessage());
            return response()->json(['message' => 'Internal Server Error'], 500);
        }
    }
}
