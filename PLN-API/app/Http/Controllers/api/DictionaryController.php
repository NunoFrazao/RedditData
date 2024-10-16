<?php

namespace App\Http\Controllers\api;

use App\Http\Controllers\Controller;
use App\Models\Dictionary;
use Illuminate\Http\Request;

class DictionaryController extends Controller
{
    public function index($userId)
    {
        $queries = Dictionary::where('user_id', $userId)->get();

        return response()->json($queries);
    }

    public function store(Request $request)
    {
        $queries = $request->input('queries', []);
        $userId = $request->input('user_id');

        foreach ($queries as $query) {
            Dictionary::create([
                'query' => $query,
                'user_id' => $userId
            ]);
        }

        return response()->json(['message' => 'Dictionary created successfully']);
    }

    public function destroy($userId)
    {
        Dictionary::where('user_id', $userId)->delete();

        return response()->json(['message' => 'Dictionary deleted successfully']);
    }
}
