#require 'fileutils'
#
## Get all files in the current directory (excluding folders)
#files = Dir.glob('*').select { |f| File.file?(f) }
#
## Rename each file to a number starting from 1
#files.each_with_index do |file, index|
#  ext = File.extname(file)  # Preserve file extension
#  new_name = "#{index + 1}#{ext}"
#
#  # Avoid renaming a file to its current name
#  unless file == new_name
#    FileUtils.mv(file, new_name)
#    puts "Renamed #{file} to #{new_name}"
#  end
#end
#
nmb = 10

while true
  result = `python clientcomfyapp.py --prompt #{nmb}.jpg --dev`
  if nmb == 68 
    break
  end
  nmb +=1
end
