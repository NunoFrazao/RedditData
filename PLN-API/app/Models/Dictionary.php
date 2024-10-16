<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Dictionary extends Model
{
    use HasFactory;

    protected $table = 'dicionario';

    protected $fillable = ['query', 'user_id'];

    public function user()
    {
        return $this->belongsTo(User::class);
    }
}
