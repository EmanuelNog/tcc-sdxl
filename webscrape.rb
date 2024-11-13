require 'nokogiri'
require 'open-uri'
require 'fileutils'
require 'selenium-webdriver'

# URL of the website to scrape
#url = 'http://www.mypecs.com/Search.aspx?catid=0&keywords=' #all
#url = 'http://www.mypecs.com/Search.aspx?catid=46&isParent=true' #activities
#url = 'http://www.mypecs.com/Search.aspx?catid=30&isParent=true' #communication
url = 'http://www.mypecs.com/Search.aspx?catid=33&isParent=true' #self_help

# Create a directory to store the downloaded images
FileUtils.mkdir_p('pecs_images')

# Set up Selenium WebDriver
options = Selenium::WebDriver::Chrome::Options.new
options.add_argument('--headless')
driver = Selenium::WebDriver.for :chrome, options: options

# Navigate to the initial URL
driver.get(url)

total_images = 0
page_number = 1
previous_first_image_name = nil

loop do
  # Parse the current page's HTML
  doc = Nokogiri::HTML(driver.page_source)

  # Find the table with id="ContentPlaceHolder1_dlData"
  table = doc.at_css('#ContentPlaceHolder1_dlData')

  if table
    first_image_name = nil

    # Iterate through the images (0 to 14)
    (0..14).each do |i|
      begin
        # Find the image title element
        title_element = driver.find_element(id: "ContentPlaceHolder1_dlData_hlnkTitle_#{i}")
        image_name = title_element.text.gsub(/[^0-9A-Za-z]/, '_')

        # Store the first image name of the page
        first_image_name = image_name if i == 0

        # Find the corresponding image element
        img = driver.find_element(id: "ContentPlaceHolder1_dlData_imgCover_#{i}")
        image_url = img.attribute('src')

        # Construct the full URL if it's a relative path
        image_url = URI.join(url, image_url).to_s unless image_url.start_with?('http')

        # Download the image
        File.open("pecs_images/#{image_name}.jpg", 'wb') do |file|
          file.write URI.open(image_url).read
        end
        puts "Downloaded: #{image_name}"
        total_images += 1
      rescue Selenium::WebDriver::Error::NoSuchElementError
        # If we can't find an element, we've likely reached the end of images on this page
        break
      rescue OpenURI::HTTPError => e
        puts "Error downloading #{image_name}: #{e.message}"
      end
    end

    puts "Downloaded images from page #{page_number}"
    page_number += 1

    # Check if we've reached the end of pagination
    if previous_first_image_name == first_image_name
      puts "Reached the end of pagination. The first image name is the same as the previous page."
      break
    end

    previous_first_image_name = first_image_name

    # Try to find and click the next button
    begin
      next_button = driver.find_element(id: 'ContentPlaceHolder1_aNext')
      next_button.click
      sleep 2 # Wait for the page to load
    rescue Selenium::WebDriver::Error::NoSuchElementError
      puts "No more pages to scrape."
      break
    end
  else
    puts "Table with id 'ContentPlaceHolder1_dlData' not found."
    break
  end
end

puts "Finished downloading #{total_images} images in total."

# Close the browser
driver.quit
