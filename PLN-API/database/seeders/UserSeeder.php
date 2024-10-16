<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Str;

class UserSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        DB::table('users')->insert([
            'name' => 'Nuno asd Frazão',
            'email' => 'a1@gmail.pt',
            'tipo_user' => '1',
            'password' => Hash::make('123456'),
            'contacto' => '911111111'
        ]);

        DB::table('users')->insert([
            'name' => 'José asd asd Parreira',
            'email' => 'a2@gmail.pt',
            'tipo_user' => '1',
            'password' => Hash::make('123456'),
            'contacto' => '911111111'
        ]);

        for ($i = 0; $i < 10; $i++) {
            DB::table('users')->insert([
                'name' => Str::random(10),
                'email' => Str::random(10) . '@example.com',
                'password' => Hash::make('123456'),
                'contacto' => $this->generatePhoneNumber()
            ]);
        }
    }

    /**
     * Generate a random phone number with an emphasis on Portuguese formats.
     */
    private function generatePhoneNumber(): string
    {
        $patterns = [
            // Portugal formats
            '+351 9' . rand(10000000, 99999999), // +351 9XXXXXXXX
            '9' . rand(10000000, 99999999), // 9XXXXXXXX

            // Other common international formats
            '+1 ' . rand(100, 999) . '-' . rand(100, 999) . '-' . rand(1000, 9999), // +1 123-456-7890 (USA/Canada)
            '+44 ' . rand(7000, 7999) . ' ' . rand(100000, 999999), // +44 7XXX XXXXXX (UK)
            '+61 ' . rand(400, 499) . ' ' . rand(100, 999) . ' ' . rand(100, 999), // +61 4XX XXX XXX (Australia)
            '+33 ' . rand(600, 699) . ' ' . rand(100, 999) . ' ' . rand(100, 999), // +33 6XX XXX XXX (France)
        ];

        return $patterns[array_rand($patterns)];
    }
}
