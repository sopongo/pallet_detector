<?PHP
$config_admin_password = '7110eda4d09e062aa5e4a390b0a572ac0d2c0220'; // sha1('1234')
$site_config = __DIR__ . '/sites.json';
$pallet_config = __DIR__ . '/pallet_config.json';

$arr_site = [
    1 => [
        "site_name" => "PCS",
        "location"  => [
            1 => "Building 1",
            2 => "Building 2",
            3 => "Building 3",
            4 => "Building 4",
            5 => "Building 5",
            6 => "Building 6",
            7 => "Building 7",
            8 => "Building 8",
            9 => "Building 9"
        ]
    ],
    2 => [
        "site_name" => "PACT",
        "location"  => [
            1 => "Loading Area",
        ]
        ],
    3 => [
        "site_name" => "PACM",
        "location"  => [
            1 => "Loading Area",
        ]
    ],
    4 => [
        "site_name" => "PACA",
        "location"  => [
            1 => "Loading Area",
        ]
    ],
    5 => [
        "site_name" => "PACK",
        "location"  => [
            1 => "Loading Area",
        ]
    ],
    6 => [
        "site_name" => "PACJ",
        "location"  => [
            1 => "Building 1",
            2 => "Building 2",
        ]
    ],
    7 => [
        "site_name" => "PACS",
        "location"  => [
            1 => "Building 1",
            2 => "Building 2",
        ]
    ],
    8 => [
        "site_name" => "PACR",
        "location"  => [
            1 => "Loading Area",
        ]
    ],
];

// เขียน array เป็น JSON file
//$json_path = __DIR__ . '/sites.json';
//file_put_contents($json_path, json_encode($arr_site, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
?>