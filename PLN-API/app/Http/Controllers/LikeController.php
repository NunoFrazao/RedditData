<?php

namespace App\Http\Controllers;

use App\Http\Resources\LikeResource;
use App\Models\Like;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Auth;

class LikeController extends Controller
{
    public function like(Request $request)
    {
        return $this->handleLikeDislike($request, 1);
    }

    public function dislike(Request $request)
    {
        return $this->handleLikeDislike($request, -1);
    }

    private function handleLikeDislike(Request $request, $likeValue)
    {
        // Validate the incoming request
        $validated = $request->validate([
            'post_id' => 'required|string',
            'user_id' => 'required|integer'
        ]);

        $postId = $validated['post_id'];
        $userId = $validated['user_id'];

        // Log the received data for debugging
        //Log::info('Received like/dislike request', ['user_id' => $userId, 'post_id' => $postId, 'like_value' => $likeValue]);

        // Update or create the like/dislike record
        $like = Like::updateOrCreate(
            ['user_id' => $userId, 'post_id' => $postId],
            ['like' => $likeValue]
        );

        return response()->json(['success' => true, 'message' => 'Action recorded']);
    }

    public function getLikesByPostId($postId, Request $request)
    {
        $userId = $request->input('user_id');

        $likes = Like::where('post_id', $postId)
            ->selectRaw('SUM(`like` = 1) as likes, SUM(`like` = -1) as dislikes')
            ->first();

        $userLike = Like::where('post_id', $postId)
            ->where('user_id', $userId)
            ->first();

        return response()->json([
            'post_id' => $postId,
            'likes' => $likes->likes ?? 0,
            'dislikes' => $likes->dislikes ?? 0,
            'user_like' => $userLike ? $userLike->like : 0
        ]);
    }

    public function neutral(Request $request)
    {
        // Validate the incoming request
        $validated = $request->validate([
            'post_id' => 'required|string',
            'user_id' => 'required|integer'
        ]);

        $postId = $validated['post_id'];
        $userId = $validated['user_id'];

        // Remove the like/dislike record
        Like::where('user_id', $userId)
            ->where('post_id', $postId)
            ->delete();

        return response()->json(['success' => true, 'message' => 'Action removed']);
    }
}
