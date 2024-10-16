<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\api\UserController;
use App\Http\Controllers\api\RedditController;
use App\Http\Controllers\LikeController;
use App\Http\Controllers\api\DictionaryController;

// Reddit routes
Route::get('/get_access_token', [RedditController::class, 'getAccessToken']);
Route::post('/get_data', [RedditController::class, 'getData']);
Route::get('/comments/{post_id}', [RedditController::class, 'getComments']);
Route::get('/analyze_comments', [RedditController::class, 'analyzeComments']);

Route::post('/analyze', [RedditController::class, 'analyze']); /* Leandro Vieira Modulo 2 */
Route::post('/analyze/vader', [RedditController::class, 'analyzeVader']); /* Leandro Vieira Modulo 2 */

// User routes
Route::get('users/id/{id}', [UserController::class, 'getUserById']);
Route::post('users/email', [UserController::class, 'getUser']);
Route::delete('/users/delete-account/{id}', [UserController::class, 'deleteAccount']);
Route::apiResource('users', UserController::class);

Route::get('/admin-count', [UserController::class, 'getAdminCount']);

Route::post('/get_likes_dislikes', [RedditController::class, 'getLikesDislikes']);
Route::post('/like', [LikeController::class, 'like'])->name('like');
Route::post('/dislike', [LikeController::class, 'dislike'])->name('dislike');
Route::post('/neutral', [LikeController::class, 'neutral'])->name('neutral');
Route::get('/likes/{post_id}', [LikeController::class, 'getLikesByPostId']);

Route::get('/userLikes/{user_id}', [LikeController::class, 'getUserLikes']);
Route::get('user-likes-posts/{userId}', [RedditController::class, 'getUserLikesAndPosts']);

Route::get('/dictionary/{userId}', [DictionaryController::class, 'index']);
Route::post('/dictionary', [DictionaryController::class, 'store']);
Route::delete('/dictionary/{userId}', [DictionaryController::class, 'destroy']);

Route::post('/users/history', [UserController::class, 'storeHistory']);
Route::get('/users/history/{user_id}', [UserController::class, 'getHistoryByUserId']);

Route::get('/searches-per-month', [UserController::class, 'getSearchesPerDay']);
Route::get('/users-count-for-comparison', [UserController::class, 'getUsersCountForComparison']);
Route::get('/posts-likes-dislikes-history', [UserController::class, 'getPostsLikesDislikesHistory']);

/*
Route::middleware('auth:sanctum')->get('/user', function (Request $request) {
    return $request->user();
});
*/
